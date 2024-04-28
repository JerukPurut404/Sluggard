import requests

class Sluggard:
    def __init__(self, csrf_token, cookies):
        self.url = "https://api.simulise.com/graphql"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "Content-Disposition": None,
            "x-csrf-token": csrf_token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": cookies
        }

    def debug_mode(self, input):
        data = {"query": input}
        response = requests.post(self.url, headers=self.headers, json=data)
        response_json = response.json()
        return response_json
        

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
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def get_portfolio_banner(self):
        data = {"query": "query getPortfolioBannerForSettings {\n viewer {\n id\n portfolioBanner {\n ...portfolioBannerFields\n __typename\n }\n __typename\n }\n staticPortfolioBanners {\n ...staticPortfolioBannerFields\n __typename\n }\n}\n\nfragment portfolioBannerFields on PortfolioBanner {\n ... on MedialibraryFile {\n id\n url\n __typename\n }\n ... on StaticPortfolioBanner {\n ...staticPortfolioBannerFields\n __typename\n }\n __typename\n}\n\nfragment staticPortfolioBannerFields on StaticPortfolioBanner {\n key\n url\n name\n group\n __typename\n}"}
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            banner_info = {
                'user_id': response_json['data']['viewer']['portfolioBanner']['id'],
                'banner_url': response_json['data']['viewer']['portfolioBanner']['url'],
                'static_banners': []
            }

            static_banners = []
            for banner in response_json['data']['staticPortfolioBanners']:
                banner_data = {
                    'banner_filename': banner['key'],
                    'banner_url': banner['url'],
                    'banner_name': banner['name'],
                    'banner_group': banner['group']
                }
                static_banners.append(banner_data)
            banner_info['static_banners'] = static_banners
            return banner_info
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def get_unsplash_banner(self, query, first=int, page=int):
        data = {"query": "query medialibraryPagedUnsplashImages($query: String, $first: Int!, $page: Int!) {\n unsplashImages: medialibraryUnsplashSearch(\n query: $query\n first: $first\n page: $page\n ) {\n data {\n id\n user {\n id\n name\n permalink\n __typename\n }\n title\n preview\n blurHash\n permalink\n createdAt\n aspectRatio\n description\n downloadUrl\n __typename\n }\n paginatorInfo {\n hasMorePages\n __typename\n }\n __typename\n }\n}", "variables": {"page": page, "first": first, "query":query}}
        try: 
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            
            unsplash_info = {
                'unsplash_data': []
            }

            unsplash_data = []
            for data in response_json['data']['unsplashImages']['data']:
                picture_data = {
                    'picture_id': data['id'],
                    'picture_title': data['title'],
                    'picture_preview': data['preview'],
                    'picture_permalink': data['permalink'],
                    'picture_date': data['createdAt'],
                    'picture_aspectRatio': data['aspectRatio'],
                    'picture_description': data['description'],
                    'picture_downloadLink': data['downloadUrl'],
                    'unsplash_userId': data['user']['id'],
                    'unsplash_name': data['user']['name'],
                    'unsplash_permalink': data['user']['permalink']
                }
                unsplash_data.append(picture_data)
            unsplash_info['unsplash_data'] = unsplash_data
            return unsplash_info
        except requests.exceptions.RequestException as e:
                return f"An error occurred: {e}" 

    def add_banner_from_unsplash(self, picture_id):
        data = {"query": "mutation medialibraryImportFromUnsplash($input: MedialibraryImportFromUnsplashInput!) {\n response: medialibraryImportFromUnsplash(input: $input) {\n file {\n ...medialibraryFilesFileFieldsFragment\n __typename\n }\n ...mutationFields\n __typename\n }\n}\n\nfragment medialibraryFilesFileFieldsFragment on MedialibraryFile {\n id\n size\n type\n icon\n title\n uploader {\n id\n name\n permalink\n __typename\n }\n extension\n createdAt\n thumbnail\n downloadUrl\n canBeEdited\n canBeDeleted\n thumbnailBlurHash\n renderedPreviewUrl\n __typename\n}\n\nfragment mutationFields on MutationPayload {\n status {\n success\n errors {\n name\n messages\n __typename\n }\n __typename\n }\n __typename\n}", "variables": {"input": {"id": picture_id, "context": "USER"}}}
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            banner_info = {
                'file_id': response_json['data']['response']['file']['id'],
                'file_size': response_json['data']['response']['file']['size'],
                'file_title': response_json['data']['response']['file']['title'] 
            }
            return banner_info
        except requests.exceptions.RequestException as e:
                return f"An error occurred: {e}" 

    def get_banner_library(self, first=20, page=1, query=""):
        data = {"query": "query medialibraryPagedFiles($context: MedialibraryContext, $query: String, $types: [MedialibraryFileType!], $first: Int!, $page: Int!) {\n medialibraryFiles(\n context: $context\n query: $query\n types: $types\n first: $first\n page: $page\n ) {\n data {\n ...medialibraryFilesFileFieldsFragment\n __typename\n }\n paginatorInfo {\n hasMorePages\n __typename\n }\n __typename\n }\n}\n\nfragment medialibraryFilesFileFieldsFragment on MedialibraryFile {\n id\n size\n type\n icon\n title\n uploader {\n id\n name\n permalink\n __typename\n }\n extension\n createdAt\n thumbnail\n downloadUrl\n canBeEdited\n canBeDeleted\n thumbnailBlurHash\n renderedPreviewUrl\n __typename\n}", "variables": {"page":page, "first": first, "query": query, "types":["IMAGE"], "context": "USER"}}
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            library_info = {
                'images_data': []
            }

            images_data = []
            for data in response_json['data']['medialibraryFiles']['data']:
                image_data = {
                    "image_id": data['id'],
                    "image_size": data['size'],
                    "image_title": data['title'],
                    "image_date": data['createdAt'],
                    "image_previewLink": data['thumbnail'],
                    "image_downloadLink": data['downloadUrl'],
                    "image_renderedLink": data['renderedPreviewUrl'],
                    "image_uploader_id": data['uploader']['id'],
                    "image_uploader_name": data['uploader']['name'],
                    "image_uploader_permalink": data['uploader']['permalink']
                }
                images_data.append(image_data)
            library_info["images_data"] = images_data
            return library_info
        except requests.exceptions.RequestException as e:
                return f"An error occurred: {e}" 


    def delete_picture_banner(self, image_id):
        data = {
            "query": "mutation medialibraryDeleteFile($input: MedialibraryFileDeleteInput!) {\n response: medialibraryFileDelete(input: $input) {\n ...mutationFields\n __typename\n }\n}\n\nfragment mutationFields on MutationPayload {\n status {\n success\n errors {\n name\n messages\n __typename\n }\n __typename\n }\n __typename\n}",
            "variables": {"input": {"id": image_id, "context": "USER"}}
        }
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            response_data = response_json.get('data', {})
            response_status = response_data.get('response', {}).get('status', {})

            if response_status.get('success', False):
                delete_info = {
                    'Status': response_status.get('success'),
                    'Error': None
                }
            else:
                error_messages = response_status.get('errors', [])
                error_list = [{'name': error['name'], 'messages': error['messages'][0]} for error in error_messages]
                delete_info = {
                    'Status': response_status.get('success', False),
                    'Errors': error_list
                }
                
            return delete_info
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    # def upload_portfolio_banner(self, filename):
    #     # Define the operations part of the request
    #     operations = "mutation medialibraryUploadFile($input: MedialibraryUploadFileInput!) {\n  response: medialibraryUploadFile(input: $input) {\n    file {\n      ...medialibraryFilesFileFieldsFragment\n      __typename\n    }\n    ...mutationFields\n    __typename\n  }\n}\n\nfragment medialibraryFilesFileFieldsFragment on MedialibraryFile {\n  id\n  size\n  type\n  icon\n  title\n  uploader {\n    id\n    name\n    permalink\n    __typename\n  }\n  extension\n  createdAt\n  thumbnail\n  downloadUrl\n  canBeEdited\n  canBeDeleted\n  thumbnailBlurHash\n  renderedPreviewUrl\n  __typename\n}\n\nfragment mutationFields on MutationPayload {\n  status {\n    success\n    errors {\n      name\n      messages\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"

    #     # Define the map part of the request
    #     map_data = {
    #         '1': ['variables.input.file']
    #     }

    #     # Prepare the multipart/form-data request
    #     files = {
    #         'operations': (operations),
    #         'map': (str(map_data)),
    #         '1': (filename, open(filename, 'rb'), 'image/jpeg')
    #     }

    #     # Send the request
    #     response = requests.post(self.url, headers=self.headers, files=files)
    #     print(files)

    #     # Ensure the file is closed after the request
    #     files['1'][1].close()

    #     # Print the response for debugging
    #     print(response.text)

    #     # Parse and return the JSON response
    #     response_json = response.json()
    #     return response_json
