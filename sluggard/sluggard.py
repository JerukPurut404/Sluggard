import requests
import json
import re
from .user import User
from .school import School
from .community import Community
from .portfolio import Portfolio, Banner
from .exceptions import sluggardException
from .utils import get_value_deep_key

class Sluggard:
    loads = json.loads
    dumps = json.dumps
    def __init__(self, csrf_token="", cookie="", tenant=""):
        self.last_response = {}
        self.url = "https://api.simulise.com/graphql"
        self.tenant_url = f'https://{tenant}.simulise.com'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "Content-Disposition": None,
            "x-csrf-token": csrf_token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": f'simulise_session_production={cookie}; simulise_legacy_session_production={cookie};',
            "DNT": "1"
        }

        self.session = requests.Session()
                

    def school_name_search(self, name):
        data = {"query":"query authenticationRealmSearch($query: String!) {\n  authenticationRealmSearch(query: $query) {\n    ...authenticationRealmFields\n    __typename\n  }\n}\n\nfragment authenticationRealmFields on AuthenticationRealm {\n  id\n  key\n  sso\n  idp {\n    name\n    logo\n    __typename\n  }\n  logo\n  name\n  i18n {\n    lang\n    type\n    __typename\n  }\n  alias\n  permalink\n  __typename\n}", "variables":{"query":name}}
        try:
            response = self.session.post(self.url, json=data)
            response_json = response.json()

            for info in response_json['data']['authenticationRealmSearch']:
                school_info = {
                    'id': info['id'],
                    'key': info['key'],
                    'sso': info['sso'],
                    'idp_name': info['idp']['name'],
                    'idp_logo': info['idp']['logo'],
                    'school_logo': info['logo'],
                    'school_name': info['name'],
                    'school_permalink': info['permalink']
                }
            return School.search__from__dict(school_info)
        except requests.exceptions.RequestException as e:
            raise sluggardException("Request failed") from e
    
    def discover_user(self, user):
        data = {"query": f"query dashboardDiscoverUser($id: String!) {{ user(id: $id) {{ id username primaryRole groupsActive {{ ...dashboardUserTileGroupsFragment __typename }} dashboardTiles {{ id key title isHidden canBeHidden __typename }} __typename }} viewer {{ id tenant {{ id settings {{ goalsLargerOnDashboard __typename }} __typename }} username primaryRole groupsActive {{ ...dashboardUserTileGroupsFragment __typename }} externalInvitationCount __typename }} }} fragment dashboardUserTileGroupsFragment on Group {{ __typename ... on Entity {{ id __typename }} ... on WorkGroup {{ id name icon permalink __typename }} ... on SchoolGroup {{ id name icon path permalink __typename }} ... on VirtualGroup {{ id name icon permalink __typename }} }}" , "variables": {"id": user}}
        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            return User.discover_from_dict(response_json)
        except requests.exceptions.RequestException as e:
            raise sluggardException("Request failed") from e

    def get_community_recent_post(self, user):
        data = {"query": "query dashboardTileCommunityActivity($id: String!) {\n activity: user(id: $id) {\n id\n portfolioRecentCommunityItems {\n id\n icon\n title\n author {\n id\n name\n avatar\n username\n portfolioPermalink\n __typename\n }\n permalink\n createdAt\n __typename\n }\n __typename\n }\n}" , "variables": {"id": user}}
        try: 
            response = self.session.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            return Community.from_dict(response_json)
        except requests.exceptions.RequestException as e:
            raise sluggardException("Request failed") from e
            

    def get_community_posts(self):
        response = self.session.get(self.tenant_url + "/community/stream/filter?combine=false", headers=self.headers)
        response_json = response.json()
        pattern_activity_id = r'data-activity-id="(\d+)"'
        pattern_real_id = r'data-activity-real-id="([a-f0-9\-]+)"'
        pattern_title = r'\s*<a href=\".*?"\>(.*?)'
        pattern_title2 = r'<h3 class="font-thin m-t-none m-b-none"><a href=".*?">(.*?)</a></h3>'
        pattern_author_name = r'<a href="https:\/\/ma\.simulise\.com\/p\/\d+".*?>\s*(.*?)\s*'
        pattern_timestamp = r'<time class="timeago" data-toggle="tooltip" title="(\d{2}-\d{2}-\d{4} \d{2}:\d{2})" datetime=".*?"'
        pattern_content = r'<p class="m-b-none">\s*(.*?)\s*<\/p>'
        pattern_tags = r'<a href="#".*?>(.*?)<\/a>'
        pattern_image_link = r'background: url\((.*?)\) no-repeat center;' 
    
        activity_ids = re.findall(pattern_activity_id, response_json['elements'])
        real_ids = re.findall(pattern_real_id, response_json['elements'])
        titles = re.findall(pattern_title, response_json['elements'])
        author_names = re.findall(pattern_author_name, response_json['elements'])
        timestamps = re.findall(pattern_timestamp, response_json['elements'])
        contents = re.findall(pattern_content, response_json['elements'])
        tags = re.findall(pattern_tags, response_json['elements'])
        image_links = re.findall(pattern_image_link, response_json['elements'])
        

        max_length = max(len(activity_ids), len(real_ids), len(titles), len(author_names), len(timestamps), len(contents), len(tags), len(image_links))
        posts = []
        for i in range(max_length):
            post = {
                "activity_id": activity_ids[i] if i < len(activity_ids) else None,
                "real_id": real_ids[i] if i < len(real_ids) else None,
                "title": titles[i] if i < len(titles) else None,
                "author": {
                    "name": author_names[i] if i < len(author_names) else None,
                },
                "timestamp": timestamps[i] if i < len(timestamps) else None,
                "content": contents[i] if i < len(contents) else None,
                "tags": tags[i].split(', ') if i < len(tags) else None,
                "image_link": image_links[i] if i < len(image_links) else None,
            }
            posts.append(post)

        json_data = json.dumps(posts, indent=4)

        print(json_data)

    def get_portfolio_items(self, user):
        try:
            data = {
                "query": "query dashboardTilePortfolioItems($id: String!) {\n  dashboard: user(id: $id) {\n    id\n    portfolioItems(first: 5) {\n      data {\n        id\n        icon\n        title\n        author {\n          id\n          name\n          __typename\n        }\n        permalink\n        createdAt\n        __typename\n      }\n      paginatorInfo {\n        total\n        __typename\n      }\n      __typename\n    }\n    portfolioPermalink\n    __typename\n  }\n}",
                "variables": {"id": user}
            }
            response = self.session.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
    
            return User.portfolio_from_dict(response_json)
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"


    def user_info(self, user_id):
        try:
            data = {
                "query": "query dashboardTileProfile($id: String!, $lookingAtOwnProfile: Boolean!, $viewingExternal: Boolean!) { dashboard: user(id: $id) { id name about avatar username external @include(if: $viewingExternal) firstname primaryRole renderedLabel externalInvited @include(if: $viewingExternal) changelogsUnread @include(if: $lookingAtOwnProfile) canBeImpersonated @skip(if: $lookingAtOwnProfile) profileCompletion @include(if: $lookingAtOwnProfile) { actions { action completed translation __typename } percentage __typename } __typename } }",
                "variables": {"id": user_id, "lookingAtOwnProfile": False, "viewingExternal": False}
            }
            
            response = self.session.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            user_data = response_json.get('data', {}).get('dashboard', {})
            
            user_info = {
                'id': user_data.get('id', ''),
                'avatar': user_data.get('avatar', ''),
                'name': user_data.get('name', ''),
                'about': user_data.get('about', ''),
                'username': user_data.get('username', ''),
                'primary_role': user_data.get('primaryRole', ''),
                'render_label': user_data.get('renderedLabel', ''),
                'canBeImposter': user_data.get('canBeImpersonated', '')
            }
            
            return User.info_from_dict(user_info)
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def user_assignments(self, user_id, page=int):
        filters = ["status:doover,finished_not_handed_in,in_progress,past_able_hand_in,pending,under_review"]
        
        data = {
            "query": "query userAssignedAssignments($userId: String!, $page: Int!, $filters: [String!]!, $orderBy: UserAssignedAssignmentsOrder) {\n  result: user(id: $userId) {\n    id\n    ...userAssignmentsAssignedContainer\n    __typename\n  }\n}\n\nfragment userAssignmentsAssignedContainer on User {\n  assignmentsAssignedContainer(page: $page, filters: $filters, orderBy: $orderBy) {\n    data {\n      __typename\n      ... on AssignedAssignment {\n        id\n        plan {\n          id\n          title\n          __typename\n        }\n        state\n        isLate\n        endDate\n        canHandIn\n        permalink\n        assignedAt\n        approvedAt\n        assignment {\n          id\n          icon\n          title\n          cover {\n            thumbnail\n            __typename\n          }\n          subjects: labels(only: [SUBJECTS]) {\n            id\n            name\n            topic {\n              id\n              __typename\n            }\n            abbreviation\n            autocompletion {\n              id\n              text\n              caption\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        deliveredAt\n        statusMessage {\n          text\n          color\n          status\n          shortText\n          __typename\n        }\n        totalDeliverables\n        deliveredDeliverables\n        assignedAssignmentPlan {\n          id\n          permalink\n          __typename\n        }\n        __typename\n      }\n      ... on AssignedAssignmentGroup {\n        id\n        plan {\n          id\n          title\n          __typename\n        }\n        state\n        endDate\n        statusMessage {\n          color\n          shortText\n          __typename\n        }\n        minAssignments\n        assignedAssignments {\n          id\n          state\n          isLate\n          permalink\n          canHandIn\n          assignedAt\n          approvedAt\n          assignment {\n            id\n            title\n            subjects: labels(only: [SUBJECTS]) {\n              id\n              name\n              abbreviation\n              autocompletion {\n                id\n                text\n                caption\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          deliveredAt\n          statusMessage {\n            color\n            status\n            shortText\n            __typename\n          }\n          totalDeliverables\n          deliveredDeliverables\n          assignedAssignmentPlan {\n            id\n            permalink\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n    }\n    paginatorInfo {\n      ...paginatorFieldsFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment paginatorFieldsFragment on PaginatorInfo {\n  total\n  lastPage\n  lastItem\n  firstItem\n  currentPage\n  hasMorePages\n  __typename\n}",
            "variables": {
                "filters": filters,
                "page": page,
                "orderBy": { "field": "TITLE", "direction": "ASC" },
                "userId": user_id
            }
        } 

        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
            return User.assignments_from_dict(response.json())
        except requests.exceptions.RequestException as e:
            raise sluggardException("Request failed") from e


    # Unfinished
    def view_assignment(self, Assignedassignment_id):
        data = {"query": "query getSingleUserAssignment($assignmentAssigned: ID!) {\n  viewer {\n    username\n    assignmentAssigned(id: $assignmentAssigned) {\n      ...assignedAssignmentFields\n      __typename\n    }\n    ...assignmentAssignedUserFields\n    __typename\n  }\n}\n\nfragment assignedAssignmentFields on AssignedAssignment {\n  id\n  user {\n    ...assignmentAssignedUserFields\n    __typename\n  }\n  state\n  isLate\n  isPast\n  endDate\n  approver {\n    ...assignmentAssignedUserFields\n    __typename\n  }\n  reviewers {\n    ...assignmentAssignedUserFields\n    __typename\n  }\n  inProcess\n  startable\n  isApproved\n  isArchived\n  canReflect\n  assignment {\n    badges {\n      showPercentages\n      __typename\n    }\n    ...assignmentFields\n    ...assignmentDeliverablesFields\n    ...assignmentDeliverablePagesFields\n    __typename\n  }\n  canWithdraw\n  lastAuditLog {\n    id\n    createdAt\n    __typename\n  }\n  endDateIsSoft\n  statusMessage {\n    text\n    color\n    __typename\n  }\n  assignedBadges {\n    id\n    weight\n    badge {\n      id\n      __typename\n    }\n    __typename\n  }\n  connectableKey\n  currentReviewer {\n    ...assignmentAssignedUserFields\n    __typename\n  }\n  endDateFormatted\n  canAnswerFeedback\n  approvedAtFormatted\n  deliveredAtFormatted\n  reflectionIsOptional\n  reflectionIsOptionalAndUncompleted\n  ...assignmentUserReflectionsFields\n  ...assignedAssignmentFeedbackFields\n  ...assignmentAssignedDeliveredFields\n  ...assignedAssignmentOtherReflectionInvitationsFields\n  __typename\n}\n\nfragment assignmentAssignedUserFields on User {\n  id\n  name\n  avatar\n  username\n  permalink\n  __typename\n}\n\nfragment assignmentFields on Assignment {\n  id\n  icon\n  tags: labels(only: [TAGS]) {\n    id\n    name\n    shortName: name(length: 30)\n    ...autocompleteWithValueFieldsFragment\n    __typename\n  }\n  title\n  cover {\n    id\n    url\n    __typename\n  }\n  labels {\n    id\n    name\n    topic {\n      id\n      type\n      name\n      icon\n      color\n      __typename\n    }\n    shortName: name(length: 30)\n    ...autocompleteWithValueFieldsFragment\n    __typename\n  }\n  blocks {\n    id\n    type\n    title\n    content\n    isPresentable\n    data {\n      ... on ContentBlockSimuliseFileData {\n        id\n        file {\n          id\n          type\n          icon\n          size\n          title\n          preview\n          extension\n          downloadUrl\n          renderedPreviewUrl\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  badges {\n    id\n    name\n    type\n    levels\n    blocks {\n      id\n      type\n      content\n      __typename\n    }\n    weights {\n      color\n      level\n      title\n      image\n      percentage\n      __typename\n    }\n    criteria {\n      id\n      name\n      order\n      texts {\n        image {\n          id\n          thumbnail\n          __typename\n        }\n        level\n        formattedContent\n        __typename\n      }\n      weight\n      levels\n      __typename\n    }\n    isOptional\n    description\n    singlePointConfig {\n      negativeTitle\n      positiveTitle\n      negativeMessage\n      positiveMessage\n      __typename\n    }\n    __typename\n  }\n  subjects: labels(only: [SUBJECTS]) {\n    id\n    name\n    shortName: name(length: 30)\n    ...autocompleteWithValueFieldsFragment\n    __typename\n  }\n  resources {\n    ... on AssignmentResourceLink {\n      id\n      url\n      title\n      embed {\n        type\n        __typename\n      }\n      description\n      previewImage\n      __typename\n    }\n    ... on AssignmentResourceFile {\n      id\n      title\n      attachment {\n        id\n        icon\n        thumbnail\n        downloadUrl\n        renderedPreviewUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  isDeleted\n  isArchived\n  badgesCount\n  feedbackCount\n  reflectionOther {\n    type\n    min\n    max\n    __typename\n  }\n  optionalBadgesData {\n    min\n    max\n    __typename\n  }\n  actualDeliverablesCount\n  __typename\n}\n\nfragment assignmentDeliverablesFields on Assignment {\n  deliverables {\n    id\n    type\n    title\n    sources\n    minimum\n    maximum\n    multiple\n    template {\n      id\n      title\n      __typename\n    }\n    templates {\n      key\n      name\n      icon\n      fileType\n      __typename\n    }\n    isOptional\n    description\n    requirements\n    postMinWords\n    postMaxWords\n    plagiarismCheck {\n      enabled\n      eulaAcceptanceLabel\n      eulaAcceptanceMessage\n      eulaAcceptanceRequired\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment assignmentDeliverablePagesFields on Assignment {\n  deliverablePages {\n    id\n    type\n    title\n    sources\n    minimum\n    template {\n      id\n      title\n      createPageLink\n      formattedDescription\n      __typename\n    }\n    isOptional\n    description\n    requirements\n    plagiarismCheck {\n      enabled\n      eulaAcceptanceLabel\n      eulaAcceptanceMessage\n      eulaAcceptanceRequired\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment assignmentUserReflectionsFields on AssignedAssignment {\n  reflectionComments {\n    id\n    author {\n      ...assignmentAssignedUserFields\n      __typename\n    }\n    comment\n    createdAt\n    criterion {\n      id\n      __typename\n    }\n    __typename\n  }\n  singlePointComments {\n    id\n    author {\n      ...assignmentAssignedUserFields\n      __typename\n    }\n    negative\n    positive\n    createdAt\n    criterion {\n      id\n      __typename\n    }\n    __typename\n  }\n  reflection {\n    ...assignmentUserReflectionFields\n    __typename\n  }\n  approverReflection {\n    ...assignmentUserReflectionFields\n    __typename\n  }\n  otherReflections {\n    ...assignmentUserReflectionFields\n    __typename\n  }\n  otherReflectionUsers {\n    ...assignmentAssignedUserFields\n    ...userAutocompleteFieldsFragment\n    __typename\n  }\n  ...assignmentUserReflectionAutosaveFields\n  __typename\n}\n\nfragment assignedAssignmentFeedbackFields on AssignedAssignment {\n  feedback {\n    id\n    owner {\n      ...assignmentAssignedUserFields\n      __typename\n    }\n    files {\n      id\n      icon\n      type\n      title\n      extension\n      thumbnail\n      downloadUrl\n      renderedPreviewUrl\n      __typename\n    }\n    feedback\n    createdAt\n    __typename\n  }\n  feedbackUsed\n  hasFeedbackQuestionsLeft\n  __typename\n}\n\nfragment assignmentAssignedDeliveredFields on AssignedAssignment {\n  id\n  delivered {\n    id\n    item {\n      ... on MedialibraryFile {\n        id\n        type\n        icon\n        title\n        thumbnail\n        createdAt\n        __typename\n      }\n      ... on PortfolioPage {\n        ...deliverablePortfolioPageFields\n        __typename\n      }\n      ... on PortfolioItem {\n        ...deliverablePortfolioPostFields\n        __typename\n      }\n      __typename\n    }\n    preview\n    deliverable {\n      id\n      __typename\n    }\n    hasAnnotations\n    urkundSubmission {\n      id\n      status\n      optOut {\n        message\n        permalink\n        __typename\n      }\n      errorReason\n      __typename\n    }\n    turnitinSubmission {\n      id\n      status\n      report {\n        permalink\n        isSignificant\n        __typename\n      }\n      errorReason\n      __typename\n    }\n    supportsAnnotations\n    __typename\n  }\n  __typename\n}\n\nfragment assignedAssignmentOtherReflectionInvitationsFields on AssignedAssignment {\n  otherReflectionInvitations {\n    id\n    user {\n      ...assignmentAssignedUserFields\n      __typename\n    }\n    createdAt\n    isDeclined\n    declinedAt\n    submittedAt\n    isSubmitted\n    isProgressed\n    __typename\n  }\n  __typename\n}\n\nfragment autocompleteWithValueFieldsFragment on Autocompletable {\n  autocompletion {\n    id\n    text\n    icon\n    value\n    avatar\n    prefix\n    caption\n    __typename\n  }\n  __typename\n}\n\nfragment assignmentUserReflectionFields on AssignmentReflection {\n  id\n  data {\n    badge\n    optional\n    criteria {\n      level\n      comments {\n        id\n        comment\n        createdAt\n        __typename\n      }\n      criterion\n      singlePointComment {\n        id\n        negative\n        positive\n        createdAt\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  author {\n    ...assignmentAssignedUserFields\n    __typename\n  }\n  createdAt\n  __typename\n}\n\nfragment userAutocompleteFieldsFragment on User {\n  autocompletion {\n    id\n    text\n    icon\n    value\n    avatar\n    caption\n    __typename\n  }\n  __typename\n}\n\nfragment assignmentUserReflectionAutosaveFields on AssignedAssignment {\n  reflectionAutosaves {\n    id\n    badge {\n      id\n      name\n      __typename\n    }\n    author {\n      id\n      name\n      __typename\n    }\n    weight\n    comment\n    updatedAt\n    criterion {\n      id\n      name\n      __typename\n    }\n    negativeComment\n    positiveComment\n    __typename\n  }\n  __typename\n}\n\nfragment deliverablePortfolioPageFields on PortfolioPage {\n  id\n  title\n  icon\n  author {\n    id\n    name\n    __typename\n  }\n  template {\n    id\n    title\n    __typename\n  }\n  permalink\n  createdAt\n  featuredImage {\n    id\n    thumbnail\n    __typename\n  }\n  __typename\n}\n\nfragment deliverablePortfolioPostFields on PortfolioItem {\n  id\n  icon\n  title\n  types {\n    key\n    name\n    icon\n    fileType\n    __typename\n  }\n  author {\n    id\n    name\n    __typename\n  }\n  permalink\n  draftedAt\n  createdAt\n  previewImage\n  collaboration {\n    id\n    callaboratorCount\n    __typename\n  }\n  __typename\n}", "variables": {"assignmentAssigned": Assignedassignment_id}}
        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
            response_json = response.json()
            return User.assignments_from_dict(response_json)
        except requests.exceptions.RequestException as e:
            raise sluggardException("Request failed") from e

    def unread_notification(self):
        data = {"query":"subscription listenForUnreadNotificationChanges {\n  count: notificationsUnreadCount\n}"}
        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def get_portfolio_banner(self):
        data = {"query": "query getPortfolioBannerForSettings {\n viewer {\n id\n portfolioBanner {\n ...portfolioBannerFields\n __typename\n }\n __typename\n }\n staticPortfolioBanners {\n ...staticPortfolioBannerFields\n __typename\n }\n}\n\nfragment portfolioBannerFields on PortfolioBanner {\n ... on MedialibraryFile {\n id\n url\n __typename\n }\n ... on StaticPortfolioBanner {\n ...staticPortfolioBannerFields\n __typename\n }\n __typename\n}\n\nfragment staticPortfolioBannerFields on StaticPortfolioBanner {\n key\n url\n name\n group\n __typename\n}"}
        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
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
            return User.banner_from_dict(banner_info)
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def get_unsplash_banner(self, query, first=int, page=int):
        data = {"query": "query medialibraryPagedUnsplashImages($query: String, $first: Int!, $page: Int!) {\n unsplashImages: medialibraryUnsplashSearch(\n query: $query\n first: $first\n page: $page\n ) {\n data {\n id\n user {\n id\n name\n permalink\n __typename\n }\n title\n preview\n blurHash\n permalink\n createdAt\n aspectRatio\n description\n downloadUrl\n __typename\n }\n paginatorInfo {\n hasMorePages\n __typename\n }\n __typename\n }\n}", "variables": {"page": page, "first": first, "query":query}}
        try: 
            response = self.session.post(self.url, headers=self.headers, json=data)
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
            return User.unsplash_from_dict(unsplash_info)
        except requests.exceptions.RequestException as e:
                return f"An error occurred: {e}" 

    def add_banner_from_unsplash(self, picture_id):
        data = {"query": "mutation medialibraryImportFromUnsplash($input: MedialibraryImportFromUnsplashInput!) {\n response: medialibraryImportFromUnsplash(input: $input) {\n file {\n ...medialibraryFilesFileFieldsFragment\n __typename\n }\n ...mutationFields\n __typename\n }\n}\n\nfragment medialibraryFilesFileFieldsFragment on MedialibraryFile {\n id\n size\n type\n icon\n title\n uploader {\n id\n name\n permalink\n __typename\n }\n extension\n createdAt\n thumbnail\n downloadUrl\n canBeEdited\n canBeDeleted\n thumbnailBlurHash\n renderedPreviewUrl\n __typename\n}\n\nfragment mutationFields on MutationPayload {\n status {\n success\n errors {\n name\n messages\n __typename\n }\n __typename\n }\n __typename\n}", "variables": {"input": {"id": picture_id, "context": "USER"}}}
        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
            response_json = response.json()

            banner_info = {
                'file_id': response_json['data']['response']['file']['id'],
                'file_size': response_json['data']['response']['file']['size'],
                'file_title': response_json['data']['response']['file']['title'] 
            }
            return Banner.add_from_dict(banner_info)
        except requests.exceptions.RequestException as e:
                return f"An error occurred: {e}" 

    def get_banner_library(self, first=20, page=1, query=""):
        data = {"query": "query medialibraryPagedFiles($context: MedialibraryContext, $query: String, $types: [MedialibraryFileType!], $first: Int!, $page: Int!) {\n medialibraryFiles(\n context: $context\n query: $query\n types: $types\n first: $first\n page: $page\n ) {\n data {\n ...medialibraryFilesFileFieldsFragment\n __typename\n }\n paginatorInfo {\n hasMorePages\n __typename\n }\n __typename\n }\n}\n\nfragment medialibraryFilesFileFieldsFragment on MedialibraryFile {\n id\n size\n type\n icon\n title\n uploader {\n id\n name\n permalink\n __typename\n }\n extension\n createdAt\n thumbnail\n downloadUrl\n canBeEdited\n canBeDeleted\n thumbnailBlurHash\n renderedPreviewUrl\n __typename\n}", "variables": {"page":page, "first": first, "query": query, "types":["IMAGE"], "context": "USER"}}
        try:
            response = self.session.post(self.url, headers=self.headers, json=data)
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
            response = self.session.post(self.url, headers=self.headers, json=data)
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
    #     response = self.session.post(self.url, headers=self.headers, files=files)
    #     print(files)

    #     # Ensure the file is closed after the request
    #     files['1'][1].close()

    #     # Print the response for debugging
    #     print(response.text)

    #     # Parse and return the JSON response
    #     response_json = response.json()
    #     return response_json
