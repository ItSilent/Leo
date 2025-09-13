import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import discord

class EconomySystem:
    def __init__(self):
        self.data_dir = "bot/data"
        self.economy_file = os.path.join(self.data_dir, "economy.json")
        self.shop_file = os.path.join(self.data_dir, "shop.json")
        self.transactions_file = os.path.join(self.data_dir, "transactions.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Economy settings
        self.starting_balance = 1000
        self.daily_reward_base = 100
        self.daily_reward_max = 500
        self.level_up_bonus = 50
        self.work_cooldown = 3600  # 1 hour in seconds
        
        # Shop items - MUST be set before _init_files()
        self.default_shop_items = self._get_default_shop_items()
        
        # Initialize data files AFTER setting all attributes
        self._init_files()
        
        # Work jobs
        self.jobs = {
            "programmer": {"name": "💻 Programmer", "min_pay": 200, "max_pay": 400, "success_rate": 0.8},
            "designer": {"name": "🎨 Designer", "min_pay": 150, "max_pay": 350, "success_rate": 0.85},
            "streamer": {"name": "📺 Streamer", "min_pay": 100, "max_pay": 500, "success_rate": 0.7},
            "chef": {"name": "👨‍🍳 Chef", "min_pay": 120, "max_pay": 280, "success_rate": 0.9},
            "gamer": {"name": "🎮 Pro Gamer", "min_pay": 50, "max_pay": 600, "success_rate": 0.6},
            "teacher": {"name": "📚 Teacher", "min_pay": 180, "max_pay": 320, "success_rate": 0.95}
        }
    
    def _get_default_shop_items(self):
        """Get default shop items"""
        return {
            "🎭": {"name": "Custom Role Color", "price": 5000, "type": "role_color", "description": "Change your role color"},
            "👑": {"name": "VIP Status", "price": 10000, "type": "vip", "description": "Get VIP perks for 30 days"},
            "🎪": {"name": "Custom Title", "price": 2500, "type": "title", "description": "Set a custom title that shows in rank"},
            "🎁": {"name": "Gift Box", "price": 500, "type": "lootbox", "description": "Random reward between 100-1000 coins"},
            "🛡️": {"name": "XP Boost", "price": 1500, "type": "xp_boost", "description": "2x XP for 24 hours"},
            "🎯": {"name": "Daily Streak Protection", "price": 800, "type": "streak_shield", "description": "Protect your daily streak once"}
        }
    
    def _init_files(self):
        """Initialize JSON data files"""
        # Initialize economy file
        if not os.path.exists(self.economy_file):
            with open(self.economy_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        # Initialize shop file with default items
        if not os.path.exists(self.shop_file):
            with open(self.shop_file, 'w') as f:
                json.dump(self.default_shop_items, f, indent=2)
        
        # Initialize transactions file
        if not os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _load_data(self, file_path: str) -> dict:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: str, data: dict):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_data(self, guild_id: int, user_id: int) -> dict:
        """Get user's economy data"""
        data = self._load_data(self.economy_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in data:
            data[guild_str] = {}
        
        if user_str not in data[guild_str]:
            data[guild_str][user_str] = {
                "balance": self.starting_balance,
                "bank": 0,
                "total_earned": self.starting_balance,
                "total_spent": 0,
                "daily_streak": 0,
                "last_daily": 0,
                "last_work": 0,
                "inventory": {},
                "job": None,
                "job_experience": {},
                "achievements": []
            }
            self._save_data(self.economy_file, data)
        
        return data[guild_str][user_str]
    
    def update_user_data(self, guild_id: int, user_id: int, **kwargs):
        """Update user's economy data"""
        data = self._load_data(self.economy_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        user_data = self.get_user_data(guild_id, user_id)
        user_data.update(kwargs)
        data[guild_str][user_str] = user_data
        
        self._save_data(self.economy_file, data)
    
    def add_coins(self, guild_id: int, user_id: int, amount: int, reason: str = "Unknown") -> int:
        """Add coins to user's balance"""
        user_data = self.get_user_data(guild_id, user_id)
        user_data["balance"] += amount
        user_data["total_earned"] += max(0, amount)
        
        self.update_user_data(guild_id, user_id, **user_data)
        self._log_transaction(guild_id, user_id, amount, reason)
        
        return user_data["balance"]
    
    def remove_coins(self, guild_id: int, user_id: int, amount: int, reason: str = "Unknown") -> bool:
        """Remove coins from user's balance. Returns True if successful."""
        user_data = self.get_user_data(guild_id, user_id)
        
        if user_data["balance"] < amount:
            return False
        
        user_data["balance"] -= amount
        user_data["total_spent"] += amount
        
        self.update_user_data(guild_id, user_id, **user_data)
        self._log_transaction(guild_id, user_id, -amount, reason)
        
        return True
    
    def transfer_coins(self, guild_id: int, from_user: int, to_user: int, amount: int) -> bool:
        """Transfer coins between users"""
        if not self.remove_coins(guild_id, from_user, amount, f"Transfer to {to_user}"):
            return False
        
        self.add_coins(guild_id, to_user, amount, f"Transfer from {from_user}")
        return True
    
    def claim_daily(self, guild_id: int, user_id: int) -> Tuple[bool, int, int, bool]:
        """
        Claim daily reward
        Returns: (success, amount, new_streak, streak_broken)
        """
        user_data = self.get_user_data(guild_id, user_id)
        current_time = datetime.now().timestamp()
        last_daily = user_data["last_daily"]
        
        # Check if already claimed today
        if last_daily > 0:
            time_diff = current_time - last_daily
            if time_diff < 86400:  # 24 hours
                return False, 0, user_data["daily_streak"], False
        
        # Check streak
        streak_broken = False
        if last_daily > 0:
            time_diff = current_time - last_daily
            if time_diff > 172800:  # 48 hours - streak broken
                user_data["daily_streak"] = 0
                streak_broken = True
        
        # Update streak
        user_data["daily_streak"] += 1
        user_data["last_daily"] = current_time
        
        # Calculate reward
        base_reward = self.daily_reward_base
        streak_bonus = min(user_data["daily_streak"] * 10, 200)
        random_bonus = random.randint(0, 50)
        total_reward = min(base_reward + streak_bonus + random_bonus, self.daily_reward_max)
        
        # Add coins
        new_balance = self.add_coins(guild_id, user_id, total_reward, "Daily reward")
        
        return True, total_reward, user_data["daily_streak"], streak_broken
    
    def work_job(self, guild_id: int, user_id: int, job_name: str = None) -> Tuple[bool, int, str, bool]:
        """
        Work a job for coins
        Returns: (success, earnings, message, leveled_up)
        """
        user_data = self.get_user_data(guild_id, user_id)
        current_time = datetime.now().timestamp()
        
        # Check cooldown
        if current_time - user_data["last_work"] < self.work_cooldown:
            return False, 0, "You're still tired from your last job!", False
        
        # Use current job or random if not specified
        if job_name and job_name in self.jobs:
            selected_job = job_name
        elif user_data["job"]:
            selected_job = user_data["job"]
        else:
            selected_job = random.choice(list(self.jobs.keys()))
        
        job_info = self.jobs[selected_job]
        
        # Check success
        if random.random() > job_info["success_rate"]:
            user_data["last_work"] = current_time
            self.update_user_data(guild_id, user_id, **user_data)
            return True, 0, f"Your {job_info['name']} shift didn't go well. Better luck next time!", False
        
        # Calculate earnings
        base_earnings = random.randint(job_info["min_pay"], job_info["max_pay"])
        
        # Experience bonus
        if selected_job not in user_data["job_experience"]:
            user_data["job_experience"][selected_job] = 0
        
        experience = user_data["job_experience"][selected_job]
        experience_bonus = min(int(base_earnings * (experience / 100) * 0.1), base_earnings)
        total_earnings = base_earnings + experience_bonus
        
        # Add experience
        user_data["job_experience"][selected_job] += 1
        leveled_up = user_data["job_experience"][selected_job] % 10 == 0
        
        # Update data
        user_data["last_work"] = current_time
        user_data["job"] = selected_job
        
        # Add coins
        self.add_coins(guild_id, user_id, total_earnings, f"Work: {job_info['name']}")
        
        return True, total_earnings, f"Great job! You earned {total_earnings} coins working as a {job_info['name']}!", leveled_up
    
    def gamble_coinflip(self, guild_id: int, user_id: int, bet: int, choice: str) -> Tuple[bool, bool, int, str]:
        """
        Coinflip gambling
        Returns: (can_bet, won, amount_change, result)
        """
        user_data = self.get_user_data(guild_id, user_id)
        
        if user_data["balance"] < bet:
            return False, False, 0, "Insufficient funds!"
        
        # Flip coin
        result = random.choice(["heads", "tails"])
        won = choice.lower() == result
        
        if won:
            winnings = bet  # 1:1 payout
            self.add_coins(guild_id, user_id, winnings, "Coinflip win")
            return True, True, winnings, result
        else:
            self.remove_coins(guild_id, user_id, bet, "Coinflip loss")
            return True, False, -bet, result
    
    def gamble_slots(self, guild_id: int, user_id: int, bet: int) -> Tuple[bool, int, str, List[str]]:
        """
        Slot machine gambling
        Returns: (can_bet, winnings, message, slots)
        """
        user_data = self.get_user_data(guild_id, user_id)
        
        if user_data["balance"] < bet:
            return False, 0, "Insufficient funds!", []
        
        # Remove bet
        self.remove_coins(guild_id, user_id, bet, "Slots bet")
        
        # Slot symbols with different rarities
        symbols = ["🍒", "🍒", "🍒", "🍋", "🍋", "🍊", "🍊", "⭐", "💎"]
        slots = [random.choice(symbols) for _ in range(3)]
        
        # Calculate winnings
        winnings = 0
        message = ""
        
        if slots[0] == slots[1] == slots[2]:  # Three of a kind
            if slots[0] == "💎":
                winnings = bet * 50  # Jackpot!
                message = "💎 JACKPOT! 💎"
            elif slots[0] == "⭐":
                winnings = bet * 10
                message = "⭐ AMAZING! ⭐"
            elif slots[0] == "🍊":
                winnings = bet * 5
                message = "🍊 Great! 🍊"
            elif slots[0] == "🍋":
                winnings = bet * 3
                message = "🍋 Nice! 🍋"
            elif slots[0] == "🍒":
                winnings = bet * 2
                message = "🍒 Good! 🍒"
        elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:  # Two of a kind
            winnings = int(bet * 0.5)
            message = "Two of a kind!"
        else:
            message = "Better luck next time!"
        
        if winnings > 0:
            self.add_coins(guild_id, user_id, winnings, "Slots win")
        
        return True, winnings, message, slots
    
    def get_shop_items(self, guild_id: int) -> dict:
        """Get shop items for guild"""
        return self._load_data(self.shop_file)
    
    def buy_item(self, guild_id: int, user_id: int, item_id: str) -> Tuple[bool, str]:
        """Buy item from shop"""
        shop_items = self.get_shop_items(guild_id)
        
        if item_id not in shop_items:
            return False, "Item not found in shop!"
        
        item = shop_items[item_id]
        user_data = self.get_user_data(guild_id, user_id)
        
        if user_data["balance"] < item["price"]:
            return False, f"You need {item['price']} coins but only have {user_data['balance']}!"
        
        # Remove coins
        self.remove_coins(guild_id, user_id, item["price"], f"Bought {item['name']}")
        
        # Add to inventory
        if item_id not in user_data["inventory"]:
            user_data["inventory"][item_id] = 0
        user_data["inventory"][item_id] += 1
        
        self.update_user_data(guild_id, user_id, **user_data)
        
        return True, f"Successfully bought {item['name']} for {item['price']} coins!"
    
    def get_leaderboard(self, guild_id: int, category: str = "balance", limit: int = 10) -> List[Tuple[int, dict]]:
        """Get economy leaderboard"""
        data = self._load_data(self.economy_file)
        guild_str = str(guild_id)
        
        if guild_str not in data:
            return []
        
        # Sort by category
        users = [(int(user_id), user_data) for user_id, user_data in data[guild_str].items()]
        
        if category == "balance":
            users.sort(key=lambda x: x[1]["balance"], reverse=True)
        elif category == "total_earned":
            users.sort(key=lambda x: x[1]["total_earned"], reverse=True)
        elif category == "streak":
            users.sort(key=lambda x: x[1]["daily_streak"], reverse=True)
        
        return users[:limit]
    
    def _log_transaction(self, guild_id: int, user_id: int, amount: int, reason: str):
        """Log transaction for audit trail"""
        data = self._load_data(self.transactions_file)
        guild_str = str(guild_id)
        
        if guild_str not in data:
            data[guild_str] = []
        
        transaction = {
            "user_id": user_id,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        data[guild_str].append(transaction)
        
        # Keep only last 1000 transactions per guild
        if len(data[guild_str]) > 1000:
            data[guild_str] = data[guild_str][-1000:]
        
        self._save_data(self.transactions_file, data)

# Global instance
economy_system = EconomySystem()