import sys
import vk_api


if __name__ == '__main__':
    user_id = sys.argv[1]
    access_token = sys.argv[2]

    api_vk = vk_api.VkApi(token=access_token).get_api()
    friends_list = api_vk.friends.get(user_id=user_id, fields='nickname')
    friends_count = friends_list['count']

    count_output = f'Friends count: {friends_count}'
    for friend in friends_list['items']:
        output = f"{friend['first_name']} {friend['last_name']} : id={friend['id']}"
        print(output)
    print('\n' + count_output)
