import requests

class Sluggard:
    def __init__(self, csrf_token, cookies):
        self.url = "https://api.simulise.com/graphql"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "x-csrf-token": csrf_token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": cookies
        }
        

    def school_name_search(self, name):
        data = {"query":"query authenticationRealmSearch($query: String!) {\n  authenticationRealmSearch(query: $query) {\n    ...authenticationRealmFields\n    __typename\n  }\n}\n\nfragment authenticationRealmFields on AuthenticationRealm {\n  id\n  key\n  sso\n  idp {\n    name\n    logo\n    __typename\n  }\n  logo\n  name\n  i18n {\n    lang\n    type\n    __typename\n  }\n  alias\n  permalink\n  __typename\n}", "variables":{"query":name}}
        try:
            response = requests.post(self.url, json=data)
            return response.text
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"
    
    def discover_user(self, user):
        data = {"query": f"query dashboardDiscoverUser($id: String!) {{ user(id: $id) {{ id username primaryRole groupsActive {{ ...dashboardUserTileGroupsFragment __typename }} dashboardTiles {{ id key title isHidden canBeHidden __typename }} __typename }} viewer {{ id tenant {{ id settings {{ goalsLargerOnDashboard __typename }} __typename }} username primaryRole groupsActive {{ ...dashboardUserTileGroupsFragment __typename }} externalInvitationCount __typename }} }} fragment dashboardUserTileGroupsFragment on Group {{ __typename ... on Entity {{ id __typename }} ... on WorkGroup {{ id name icon permalink __typename }} ... on SchoolGroup {{ id name icon path permalink __typename }} ... on VirtualGroup {{ id name icon permalink __typename }} }}" , "variables": {"id": user}}
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            
            discover_data = {
                'id': response_json['data']['user']['id'],
                'username': response_json['data']['user']['username'],
                'primary_role': response_json['data']['user']['primaryRole'],
            }

            groups_active_data = []
            for group in response_json['data']['user']['groupsActive']:
                group_data = {
                    'id': group['id'],
                    'name': group['name'],
                    'typename': group['__typename'],
                    'icon': group['icon'],
                    'path': group['path'],
                    'link': group['permalink']
                }
                groups_active_data.append(group_data)

            dashboard_tiles_data = []
            for dashboard in response_json['data']['user']['dashboardTiles']:
                dashboard_data = {
                    'id': dashboard['id'],
                    'key': dashboard['key'],
                    'title': dashboard['title'],
                    'isHidden': dashboard['isHidden'],
                    'canBeHidden': dashboard['canBeHidden']
                }
                dashboard_tiles_data.append(dashboard_data)

            discover_data['groups_active'] = groups_active_data
            discover_data['dashboardTiles'] = dashboard_tiles_data
            return discover_data
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def get_portfolio_items(self, user):
        try:
            data = {
                "query": "query dashboardTilePortfolioItems($id: String!) {\n  dashboard: user(id: $id) {\n    id\n    portfolioItems(first: 5) {\n      data {\n        id\n        icon\n        title\n        author {\n          id\n          name\n          __typename\n        }\n        permalink\n        createdAt\n        __typename\n      }\n      paginatorInfo {\n        total\n        __typename\n      }\n      __typename\n    }\n    portfolioPermalink\n    __typename\n  }\n}",
                "variables": {"id": user}
            }
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            portfolio_items = []
            for portfolio in response_json['data']['dashboard']['portfolioItems']['data']:
                portfolio_data = {
                    'id': portfolio['id'],
                    'icon': portfolio['icon'],
                    'title': portfolio['title'],
                    'link': portfolio['permalink'],
                    'creation_date': portfolio['createdAt'],
                    'authors': []
                }
                portfolio_items.append(portfolio_data)
               
            authors_items = []
            for portfolio in response_json['data']['dashboard']['portfolioItems']['data']:
                author_data = {
                    'id': portfolio['author']['id'],
                    'name': portfolio['author']['name']
                }
                authors_items.append(author_data)
            
            portfolio_data['authors'] = authors_items
            return portfolio_items
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def user_info(self, user_id):
        try:
            data = {
                "query": "query dashboardTileProfile($id: String!, $lookingAtOwnProfile: Boolean!, $viewingExternal: Boolean!) { dashboard: user(id: $id) { id name about avatar username external @include(if: $viewingExternal) firstname primaryRole renderedLabel externalInvited @include(if: $viewingExternal) changelogsUnread @include(if: $lookingAtOwnProfile) canBeImpersonated @skip(if: $lookingAtOwnProfile) profileCompletion @include(if: $lookingAtOwnProfile) { actions { action completed translation __typename } percentage __typename } __typename } }",
                "variables": {"id": user_id, "lookingAtOwnProfile": False, "viewingExternal": False}
            }
            
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            user_data = response_json.get('data', {}).get('dashboard', {})
            
            user_info = {
                'id': user_data.get('id', ''),
                'avatar': user_data.get('avatar', ''),
                'name': user_data.get('name', ''),
                'about': user_data.get('about', ''),
                'avatar': user_data.get('avatar', ''),
                'username': user_data.get('username', ''),
                'primary_role': user_data.get('primaryRole', ''),
                'render_label': user_data.get('renderedLabel', ''),
                'canBeImposter': user_data.get('canBeImpersonated', '')
            }
            
            return user_info
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"


    def unread_notification(self):
        data = {"query":"subscription listenForUnreadNotificationChanges {\n  count: notificationsUnreadCount\n}"}
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            return response.text
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

        