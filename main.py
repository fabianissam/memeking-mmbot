from mattermostdriver import Driver
import datetime
from dateutil.relativedelta import relativedelta
import os

ALLOWED_EMOJIS = ['kekw','kekl']

driver = Driver({'token':os.environ.get('MM_TOKEN'),'scheme':'http','port':8065,'url':'localhost','base_path':'/api/v4'})

driver.login()

team_id = driver.teams.get_user_teams('me')[0]['id']

channel_id = driver.channels.get_channel_by_name(team_id=team_id, channel_name='OT-Wissensaustausch')['id']

min_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=1) # datetime.datetime(2025, 5, 1)
since_timestamp = int(min_date.timestamp() * 1000)  # ms

posts = driver.posts.get_posts_for_channel(
    channel_id=channel_id,
    params={'page':0, 'per_page':10000, 'since': since_timestamp}
)

user_reaction_map = {}

for post in posts['posts']:
    # blacklist for users that already reacted on the post with another emoji
    reaction_user_blacklist= []
     
    user_id = posts['posts'][post]['user_id']
    if user_id not in user_reaction_map:
        user_reaction_map[user_id] = 0
    
    # if the post has no reaction just move on to the next post
    if 'reactions' not in posts['posts'][post]['metadata']:
        continue
    # iterate all reactions for a post
    for reaction in posts['posts'][post]['metadata']['reactions']:
        if reaction['emoji_name'] in ALLOWED_EMOJIS and user_id not in reaction_user_blacklist:
            reaction_user_blacklist.append(user_id)
            user_reaction_map[user_id] += 1
    
user_reaction_map = dict(sorted(user_reaction_map.items(), key=lambda item: item[1], reverse=True))
print(user_reaction_map)
message = 'Das sind die Resultate des monatlichen Memekings:\n\n'

for user in user_reaction_map:
    username = driver.users.get_user(user)['username']
    message += f'{username}: {user_reaction_map[user]} \n'

message += '\nHerzlichen Glückwunsch an '
message += driver.users.get_user(list(user_reaction_map.keys())[0])['username'] 
message += ' du bist der Memeking diesen Monats!'

driver.posts.create_post(options={'channel_id': channel_id, 'message': message})

driver.logout()