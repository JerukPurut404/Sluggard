from .group import Group
from .dashboard import Dashboard
from .assignments import Assignment
from .portfolio import Portfolio, Banner, Unsplash
from .exceptions import sluggardException

class User:
    def __init__(
        self, 
        user_id: str = None,
        username: str = None,
        primary_role: str = None,
        name: str = None,
        email: str = None,
        firstname: str = None,
        lastname: str = None,
        avatar: str = None,
        about: str = None,
        label: str = None,
        permalink: str = None,
        render_label: str = None,
        canBeImposter: str = None,
        groups: list[Group] = None,
        dashboards: list[Dashboard] = None,
        portfolios: list[Portfolio] = None,
        unsplashs: list[Unsplash] = None,
        assignments: list[Assignment] = None,
        **kwargs
    ) -> None:
        self.user_id = user_id
        self.username = username
        self.primary_role = primary_role
        self.groups = groups
        self.dashboards = dashboards
        self.portfolios = portfolios
        self.unsplashs = unsplashs
        self.assignments = assignments
        self.avatar = avatar
        self.name = name
        self.about = about
        self.render_label = render_label
        self.canBeImposter = canBeImposter
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"User({self.user_id}, {self.username}, {self.primary_role}, {self.avatar})"

    @classmethod
    def discover_from_dict(cls, raw: dict):
        user_info = raw["data"]["user"]

        groups = [
            Group(
                group_id=group.get("id"),
                name=group.get("name"),
                typename=group.get("__typename"),
                icon=group.get("icon"),
                path=group.get("path"),
                link=group.get("permalink")
            )
            for group in user_info.get("groupsActive", [])
        ]

        dashboards = [
            Dashboard(
                dashboard_id=dashboard["id"],
                key=dashboard["key"],
                title=dashboard["title"],
                isHidden=dashboard["isHidden"],
                canBeHidden=dashboard["canBeHidden"]
            )
            for dashboard in user_info.get("dashboardTiles", [])
        ]

        return cls(
            user_id=user_info.get("id"),
            username=user_info.get("username"),
            avatar=user_info.get("avatar"),
            primary_role=user_info.get("primaryRole"),
            groups=groups,
            dashboards=dashboards
        )

    @classmethod
    def info_from_dict(cls, raw: dict):
        return cls(
            user_id=raw.get('id', ''),
            avatar=raw.get('avatar', ''),
            name=raw.get('name', ''),
            about=raw.get('about', ''),
            username=raw.get('username', ''),
            primary_role=raw.get('primary_role', ''),
            render_label=raw.get('render_label', ''),
            canBeImposter=raw.get('canBeImposter', '')
        )

    @classmethod
    def banner_from_dict(cls, raw: dict):
        portfolios = [
            Portfolio(
                banner_url=raw['banner_url'],
                static_banners=raw['static_banners']
            )
        ]
        return cls(
            user_id=raw['user_id'],portfolios=portfolios
        )

    @classmethod
    def unsplash_from_dict(cls, raw: dict):
        unsplash_info = raw['unsplash_data']

        unsplashs = [Unsplash(
            unsplash_id=unsplash['picture_id'],
            title=unsplash['picture_title'],
            preview=unsplash['picture_preview'],
            perma_link=unsplash['picture_permalink'],
            date=unsplash['picture_date'],
            aspect_ratio=unsplash['picture_aspectRatio'],
            description=unsplash['picture_description'],
            download_link=unsplash['picture_downloadLink'],
            unsplash_userid=unsplash['unsplash_userId'],
            unsplash_name=unsplash['unsplash_name'],
            unsplash_permalink=unsplash['unsplash_permalink']
        )for unsplash in unsplash_info]
        return cls(unsplashs=unsplashs)

    @classmethod
    def assignments_from_dict(cls, raw: dict):
        data = raw['data']['viewer']
        assignment_assigned = data.get('assignmentAssigned', {})
        assignment_data = assignment_assigned.get('assignment', {})
        reviewer_data = assignment_assigned.get('reviewers', {})
        approver_data = assignment_assigned.get('approver', {})
        badges_data = assignment_data.get('badges', {})
        blocks_data = [badges.get('blocks', {}) for badges in badges_data]
        weights_data = [badge.get('weights', {}) for badge in badges_data]
        criteria_data = [badge.get('criteria', {}) for badge in badges_data]
        covers_data = assignment_data.get('cover', {})
        assignemnt_blocks_data = assignment_data.get('blocks', {})
        tags_data = assignment_data.get('tags', {})
        resources_data = assignment_data.get('resources', {})
        deliverable_data = assignment_data.get('deliverables', {})
        status_data = assignment_assigned.get('statusMessage')
        assignments = [
            Assignment(
                assignedassignment_id=assignment_assigned.get('id'),
                state=assignment_assigned.get('state'),
                is_late=assignment_assigned.get('isLate'),
                is_past=assignment_assigned.get('isPast'),
                end_date=assignment_assigned.get('endDate'),
                is_process=assignment_assigned.get('inProcess'),
                startable=assignment_assigned.get('startable'),
                is_approved=assignment_assigned.get('isApproved'),
                is_archived=assignment_assigned.get('isArchived'),
                can_reflect=assignment_assigned.get('canReflect'),
                can_withdraw=assignment_assigned.get('canWithdraw'),
                soft_end_date=assignment_assigned.get('endDateIsSoft'),
                connectable_key=assignment_assigned.get('connectableKey'),
                end_date_formatted=assignment_assigned.get('endDateFormatted'),
                feedback_can_answer=assignment_assigned.get('canAnswerFeedback'),
                approved_at_formatted=assignment_assigned.get('approvedAtFormatted'),
                delivered_at_formatted=assignment_assigned.get('deliveredAtFormatted'),
                optional_reflection=assignment_assigned.get('reflectionIsOptional'),
                optional_uncompleted_reflection=assignment_assigned.get('reflectionIsOptionalAndUncompleted'),
                used_feedback=assignment_assigned.get('feedbackUsed'),
                question_left_feedback=assignment_assigned.get('hasFeedbackQuestionsLeft'),
                approver_id = approver_data.get('id') if approver_data else None,
                approver_name = approver_data.get('name') if approver_data else None,
                approver_avatar = approver_data.get('avatar') if approver_data else None,
                approver_username = approver_data.get('username') if approver_data else None,
                approver_permalink = approver_data.get('permalink') if approver_data else None,               assignment_id=assignment_data.get('id'),
                icon=assignment_data.get('icon'),
                title=assignment_data.get('title'),
                is_deleted=assignment_data.get('isDeleted'),
                badges_count=assignment_data.get('badgesCount'),
                feedback_count=assignment_data.get('feedbackCount'),
                cover_id= covers_data.get('id'),
                cover_url= covers_data.get('url'),
                actual_deliverables_count=assignment_data.get('actualDeliverablesCount'),
                badges_id=[badges.get('id') for badges in badges_data],
                badges_name=[badges.get('name') for badges in badges_data],
                badges_type=[badges.get('type') for badges in badges_data],
                badges_level=[badges.get('levels') for badges in badges_data],
                badges_is_optional=[badges.get('isOptional') for badges in badges_data],
                badges_description=[badges.get('description') for badges in badges_data],
                badges_blocks_id = [block[0].get('id') for block in blocks_data],
                badges_blocks_type= [block[0].get('type') for block in blocks_data],
                badges_blocks_content= [block[0].get('content') for block in blocks_data],
                weights_color = [weight.get('color') for weight_list in weights_data for weight in weight_list],
                weights_title = [weight.get('title') for weight_list in weights_data for weight in weight_list],
                weights_level = [weight.get('level') for weight_list in weights_data for weight in weight_list],
                weights_image = [weight.get('image') for weight_list in weights_data for weight in weight_list],
                criteria_id= [criteria.get('id') for criteria_list in criteria_data for criteria in criteria_list],
                criteria_name= [criteria.get('name') for criteria_list in criteria_data for criteria in criteria_list],
                criteria_order= [criteria.get('order') for criteria_list in criteria_data for criteria in criteria_list],
                criteria_formatted_content = [text.get('formattedContent') for criteria_list in criteria_data for text in criteria_list[0].get('texts', []) if text.get('formattedContent')],
                criteria_level= [text.get('level') for criteria_list in criteria_data for text in criteria_list[0].get('texts', []) if text.get('level')],
                criteria_weight = [criteria.get('weight') for criteria_list in criteria_data for criteria in criteria_list],
                tags_id = [tag['id'] for tag in tags_data],
                tags_name= [tag['name'] for tag in tags_data],
                blocks_id= [block['id'] for block in assignemnt_blocks_data],
                blocks_type= [block['type'] for block in assignemnt_blocks_data],
                blocks_title= [block['title'] for block in assignemnt_blocks_data],
                blocks_content= [block['content'] for block in assignemnt_blocks_data],
                blocks_is_presentable= [block['isPresentable'] for block in assignemnt_blocks_data],
                resources_id= [resource.get('id') for resource in resources_data],
                resources_url= [resource.get('url') for resource in resources_data],
                resources_title= [resource.get('title') for resource in resources_data],
                deliverable_id= [deliverable.get('id') for deliverable in deliverable_data],
                deliverable_type= [deliverable.get('type') for deliverable in deliverable_data],
                deliverable_title= [deliverable.get('title') for deliverable in deliverable_data],
                deliverable_minimum= [deliverable.get('minimum') for deliverable in deliverable_data],
                deliverable_multiple= [deliverable.get('multiple') for deliverable in deliverable_data],
                deliverable_is_optional= [deliverable.get('isOptional') for deliverable in deliverable_data],
                deliverable_description= [deliverable.get('description') for deliverable in deliverable_data],
                deliverable_requirements= [deliverable.get('requirements') for deliverable in deliverable_data],
                deliverable_post_min_words= [deliverable.get('postMinWords') for deliverable in deliverable_data],
                deliverable_post_max_words= [deliverable.get('postMaxWords') for deliverable in deliverable_data],
                statusmessage_text= status_data.get('text'),
                statusmessage_color= status_data.get('color'),
                reviewer_name=[reviewer.get('name') for reviewer in reviewer_data],
                reviewer_id=[reviewer.get('id') for reviewer in reviewer_data],
                reviewer_avatar=[reviewer.get('avatar') for reviewer in reviewer_data],
                reviewer_username=[reviewer.get('username') for reviewer in reviewer_data],
                reviewer_permalink=[reviewer.get('permalink') for reviewer in reviewer_data]
            )
        ]


        return cls(
            user_id=assignment_assigned['user']['id'],
            name=assignment_assigned['user']['name'],
            username=assignment_assigned['user']['username'],
            avatar=assignment_assigned['user']['avatar'],
            permalink=assignment_assigned['user']['permalink'],
            assignments=assignments)


    @classmethod
    def portfolio_from_dict(cls, raw: dict):
        portfolio_info = raw['data']['dashboard']['portfolioItems']['data']

        portfolios = [
            Portfolio(
                portfolio_id=portfolio['id'],
                icon=portfolio['icon'],
                title=portfolio['title'],
                link=portfolio['permalink'],
                creation_date=portfolio['createdAt'],
                author_id= portfolio['author']['id'],
                author_name= portfolio['author']['name']
            )
            for portfolio in portfolio_info
        ]

        return cls(portfolios=portfolios)
