import os.path
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

credential_dir = '/home/pi/credentials/ggtasks'  # Folder containing credentials and token
creds_file = os.path.join(credential_dir, 'credentials.json')
token_file = os.path.join(credential_dir, 'token.json')


def get_task_lists():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    service = build('tasks', 'v1', credentials=creds)

    # Call the Tasks API
    tasklists = service.tasklists().list().execute()
    tasks = {}
    for tasklist in tasklists.get('items'):
        index = tasklist.get('id')
        title = tasklist.get('title')
        tasks[title] = {}
        tasks_list = service.tasks().list(tasklist=index).execute().get('items')
        parents = []
        childs = []
        for task in tasks_list:
            if 'parent' in task.keys():
                childs.append(task)
            else:
                parents.append(task)
        parents = sorted(parents, key=lambda i: i['position'])
        childs = sorted(childs, key=lambda i: i['position'])
        for task in parents+childs:
            if 'parent' in task.keys():
                tasks[title][task['parent']].append(task)
            else:
                tasks[title][task['id']] = [task]
    return(tasks)


if __name__ == '__main__':
    tasks = get_task_lists()
    # print(tasks)
    import json
    cache_file = os.path.join('/home/pi/AlarmClockProject/AlarmClock/cache/ggtasks', 'tasks.json')
    with open(cache_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(tasks, jsonfile, ensure_ascii=False, indent=4)
