from core.utils.supabase import supabase
import math

class NotificationQueueManager:
    """
    Manages the fully in-memory queues for Gold, Silver, and Bronze notification tiers.
    """
    def __init__(self):
        self.queues = {
            'gold': [],
            'silver': [],
            'bronze': []
        }

    def _get_flattened_queue_scores(self):
        """
        Chunk 1: Calculate the relative queue position for everyone currently in a queue 
        and flatten them into a single dictionary lookup: { user_id: queue_score }
        """
        master_lookup = {}
        for tier_name, queue in self.queues.items():
            total_in_queue = len(queue)
            for i, user in enumerate(queue):
                # (place in line) / (total number in queue)
                queue_score = i / total_in_queue if total_in_queue > 0 else 0.0
                master_lookup[user['id']] = queue_score
        return master_lookup

    def recalculate_tiers(self):
        """
        15-minute scheduled job to reassess all user tiers.
        """
        # 1. Flatten current state to preserve relative positions
        master_lookup = self._get_flattened_queue_scores()
        
        # 2. Fetch fresh user data from DB, already sorted by social_credit
        response = supabase.table('users') \
            .select('id, social_credit, fcm_token') \
            .not_.is_('fcm_token', 'null') \
            .order('social_credit', desc=True) \
            .execute()
            
        db_users = response.data
        if not db_users:
            self.queues = {'gold': [], 'silver': [], 'bronze': []}
            return
            
        # 3. Build unified master list with attached queue base-scores
        master_user_list = []
        for user in db_users:
            # If they were in a queue, keep their fractional score.
            # If they are brand new, drop them to the back of the line (1.0).
            queue_score = master_lookup.get(user['id'], 1.0)
            
            master_user_list.append({
                'id': user['id'],
                'fcm_token': user['fcm_token'],
                'social_credit': user['social_credit'],
                'queue_score': queue_score
            })
            
        # 4. Re-tier based on social credit limits
        total_users = len(master_user_list)
        gold_cutoff_idx = math.ceil(total_users * 0.10)
        silver_cutoff_idx = gold_cutoff_idx + math.ceil(total_users * 0.25)
        
        gold_tier = master_user_list[:gold_cutoff_idx]
        silver_tier = master_user_list[gold_cutoff_idx:silver_cutoff_idx]
        bronze_tier = master_user_list[silver_cutoff_idx:]
        
        # 5. Re-sort by queue_score (ascending) to maintain relative queue positions
        gold_tier.sort(key=lambda x: x['queue_score'])
        silver_tier.sort(key=lambda x: x['queue_score'])
        bronze_tier.sort(key=lambda x: x['queue_score'])
        
        # 6. Repopulate queues
        self.queues['gold'] = gold_tier
        self.queues['silver'] = silver_tier
        self.queues['bronze'] = bronze_tier

    def dispatch_notifications(self):
        """
        Event-driven job. Pops appropriate users off the queues, sends them to back of the line,
        and returns their fcm_tokens for the actual broadcast payload.
        """
        total_queued = sum(len(q) for q in self.queues.values())
        if total_queued == 0:
            return []
            
        # Hard limits: Either 30% of total users in current queues, or 100 people max
        global_cap = min(100, math.floor(total_queued * 0.30))
        tier_cap = math.floor(global_cap / 3)
        
        # If total user base is extremely low (e.g. 9 people), 30% is 2. floor(2/3) = 0.
        # Fallback to at least 1 person per tier if cap allows.
        if tier_cap == 0 and global_cap > 0:
            tier_cap = 1
            
        dispatch_tokens = []
        
        for tier_name in ['gold', 'silver', 'bronze']:
            queue = self.queues[tier_name]
            # Safely get up to 'tier_cap' number of users from the front
            actual_pop_count = min(tier_cap, len(queue))
            
            popped_users = queue[:actual_pop_count]
            remaining_queue = queue[actual_pop_count:]
            
            # Send popped users to the back of the line with a reset fractional score
            for user in popped_users:
                dispatch_tokens.append(user['fcm_token'])
                user['queue_score'] = 1.0
                remaining_queue.append(user)
                
            self.queues[tier_name] = remaining_queue
            
        return dispatch_tokens

# Singleton instance for the server lifecycle
queue_manager = NotificationQueueManager()
