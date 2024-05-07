class Dashboard:
    def __init__(
        self, 
        dashboard_id: str,
        key: str,
        title: str,
        isHidden: bool,
        canBeHidden: bool
        ) -> None:

        self.dashboard_id = dashboard_id
        self.key = key
        self.title = title 
        self.isHidden = isHidden
        self.canBeHidden = canBeHidden