from mattermostdriver import Driver
import datetime
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv

load_dotenv()


ALLOWED_EMOJIS = ['kekw','kekl']

driver = Driver({'token':os.getenv('MM_TOKEN'),'scheme':os.getenv('MM_SCHEME'),'port':int(os.getenv('MM_PORT')),'url':os.getenv('MM_HOST'),'base_path':os.getenv('MM_BASE_PATH')})

driver.login()

team_id = driver.teams.get_user_teams('me')[0]['id']
team_name = driver.teams.get_user_teams('me')[0]['name']

channel_id = driver.channels.get_channel_by_name(team_id=team_id, channel_name='OT-Wissensaustausch')['id']

min_date = datetime.datetime(2025, 5, 1)#datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=1) # datetime.datetime(2025, 5, 1)
since_timestamp = int(min_date.timestamp() * 1000)  # ms

posts = driver.posts.get_posts_for_channel(
    channel_id=channel_id,
    params={'page':0, 'per_page':10000, 'since': since_timestamp}
)

user_reaction_map = {}

best_meme = None
reaction_count = 0

for post in posts['posts']:
    allowed_reaction_count=0
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
        if reaction['emoji_name'] in ALLOWED_EMOJIS and reaction['user_id'] not in reaction_user_blacklist:
            allowed_reaction_count += 1
            reaction_user_blacklist.append(user_id)
            user_reaction_map[user_id] += 1
            
    if allowed_reaction_count > reaction_count:
        reaction_count = allowed_reaction_count
        best_meme = post

    
user_reaction_map = dict(sorted(user_reaction_map.items(), key=lambda item: item[1], reverse=True))
print(user_reaction_map)
message = 'Das sind die Resultate des monatlichen Memekings:\n\n'

for user in user_reaction_map:
    username = driver.users.get_user(user)['username']
    message += f'{username}: {user_reaction_map[user]} \n'

message += '\nHerzlichen Glückwunsch an '
message += driver.users.get_user(list(user_reaction_map.keys())[0])['username'] 
message += ' du bist der Memeking diesen Monats!'
message += '\n\nHier ist das Meme des Monats mit ' + reaction_count +' Reaktionen :\n\n'
message += os.getenv("MM_SCHEME")+'://'+os.getenv('MM_HOST')+':' +os.getenv("MM_PORT")+ '/'+ team_name + '/pl/' + best_meme


driver.posts.create_post(options={'channel_id': channel_id, 'message': message})

driver.logout()