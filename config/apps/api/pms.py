from .comments import CommentsMutation, CommentsQuery
from .projects import ProjectsMutation, ProjectsQuery
from .tasks import TasksMutation, TasksQuery


class PMSQuery(ProjectsQuery, TasksQuery, CommentsQuery):
    pass


class PMSMutation(ProjectsMutation, TasksMutation, CommentsMutation):
    pass
