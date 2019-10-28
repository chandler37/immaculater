"""Defines ViewFilter and its subclasses.

These allow you to filter out completed, deleted, and inactive items.

The variable CLS_BY_UI_NAME allows you to find a view filter given its
User-facing name.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from . import action
from . import ctx
from . import folder
from . import prj


class ViewFilter(object):
  """Shall we show completed items?  Inactive contexts? Etc."""

  __pychecker__ = 'unusednames=cls'

  @classmethod
  def ViewFilterUINames(cls):
    """Returns all the different aliases of this view filter.

    Returns:
      tuple(basestring)
    """
    raise NotImplementedError('ViewFilterUINames')

  def __init__(self, action_to_project, action_to_context):
    """Args:
      action_to_project: a function (Action,)->Prj raising
        ValueError if the given action does not exist.

      action_to_context: a function (Action,)->Ctx raising ValueError if the
        given action's context should exist but does not.
    """
    self.action_to_project = action_to_project
    self.action_to_context = action_to_context

  def FolderContainsShownProject(self, a_folder):
    for item in a_folder.items:
      if isinstance(item, prj.Prj) and self.ShowProject(item):
        return True
      if isinstance(item, folder.Folder) and self.ShowFolder(item):
        return True
    return False

  def ProjectContainsShownAction(self, project):
    for item in project.items:
      if self.ShowAction(item):
        return True
    return False

  def Show(self, item):
    """Returns True iff item should be displayed.

    Args:
      item: Action|Prj|Ctx|Folder
    Returns:
      bool
    """
    if isinstance(item, action.Action):
      return self.ShowAction(item)
    if isinstance(item, prj.Prj):
      return self.ShowProject(item)
    if isinstance(item, ctx.Ctx):
      return self.ShowContext(item)
    if isinstance(item, folder.Folder):
      return self.ShowFolder(item)

  def ShowAction(self, an_action):
    """Returns True iff the Action should be displayed.

    Args:
      an_action: Action
    Returns:
      bool
    """
    raise NotImplementedError

  def ShowProject(self, project):
    """Returns True iff the Prj should be displayed.

    Args:
      project: Prj
    Returns:
      bool
    """
    raise NotImplementedError

  def ShowFolder(self, a_folder):
    """Returns True iff the Folder should be displayed.

    Args:
      a_folder: Folder
    Returns:
      bool
    """
    raise NotImplementedError

  def ShowContext(self, context):
    """Returns True iff the Ctx should be displayed.

    Args:
      context: Ctx
    Returns:
      bool
    """
    raise NotImplementedError


class SearchFilter(ViewFilter):
  """Views only items matching the given search query or projects/folders
  containing matched items.

  TODO(chandler37): support "/f[^:]+b/" as "case-insensitive regex r'f[^:]+b' where dot matches newline"
  """

  @classmethod
  def ViewFilterUINames(cls):
    return tuple()

  def __init__(self, action_to_project, action_to_context, *, query, show_active, show_done):
    super().__init__(action_to_project, action_to_context)
    assert query
    self.query = query
    self.show_done = show_done
    self.show_active = show_active

  def ShowAction(self, an_action):
    containing_context = self.action_to_context(an_action)
    if bool(self.show_active) is not bool(containing_context is None or containing_context.is_active):
      return False
    if bool(self.show_done) is not bool(an_action.IsDone()):
      return False
    if self.query.lower() in an_action.name.lower():
      return True
    return an_action.note and self.query.lower() in an_action.note.lower()

  # TODO(chandler37): needs ShowNote as well -- we should not show notes that do not match the query. Further TODO: For
  # 'hypertext' commands without a search query, we should do better UI to elide notes in HTML collapsed divs if they
  # are beyond 80 characters.
  def ShowProject(self, project):
    if self.ProjectContainsShownAction(project):
      return True
    if bool(self.show_active) is not bool(project.is_active):
      return False
    if bool(self.show_done) is not bool(project.IsDone()):
      return False
    if self.query.lower() in project.name.lower():
      return True
    return project.note and self.query.lower() in project.note.lower()

  def ShowFolder(self, a_folder):
    if bool(self.show_done) is not bool(a_folder.IsDone()):
      return False
    return self.FolderContainsShownProject(a_folder) or self.query.lower() in folder.name.lower() or (
      folder.note and self.query.lower() in folder.note.lower())

  def ShowContext(self, context):
    """Override. You could argue that we should show the context if any action
    within it matches but that doesn't matter for our AsTaskPaper view of things.
    """
    if bool(self.show_active) is not bool(context.is_active):
      return False
    if bool(self.show_done) is not bool(context.IsDone()):
      return False
    return self.query.lower() in context.name.lower() or (
      context.note and self.query.lower() in context.note.lower())


class ShowAll(ViewFilter):
  """Shows all items -- doesn't filter any out."""

  @classmethod
  def ViewFilterUINames(cls):
    return ('all_even_deleted',)

  def ShowAction(self, an_action):
    return True

  def ShowProject(self, project):
    return True

  def ShowFolder(self, a_folder):
    return True

  def ShowContext(self, context):
    return True


class ShowNotDeleted(ViewFilter):
  """Shows items that are not deleted.  This WILL show inactive and
  completed items.
  """

  @classmethod
  def ViewFilterUINames(cls):
    return ('all', 'default')

  def ShowAction(self, an_action):
    return not an_action.is_deleted

  def ShowProject(self, project):
    return not project.is_deleted

  def ShowFolder(self, a_folder):
    return not a_folder.is_deleted

  def ShowContext(self, context):
    return not context.is_deleted


class ShowNotFinalized(ViewFilter):
  """Shows items that are not deleted or completed.  This WILL show
  inactive items.
  """

  @classmethod
  def ViewFilterUINames(cls):
    return ('incomplete',)

  def __init__(self, *args):
    super().__init__(*args)
    self.deleted_viewfilter = ShowNotDeleted(*args)

  def ShowAction(self, an_action):
    containing_project = self.action_to_project(an_action)
    return (self.deleted_viewfilter.ShowAction(an_action)
            and not an_action.is_complete
            and not containing_project.is_complete)

  def ShowProject(self, project):
    return (self.deleted_viewfilter.ShowProject(project)
            and not project.is_complete)

  def ShowFolder(self, a_folder):
    return self.deleted_viewfilter.ShowFolder(a_folder)

  def ShowContext(self, context):
    return self.deleted_viewfilter.ShowContext(context)


class ShowActionable(ViewFilter):
  """Shows items that are not deleted, completed, or inactive."""

  @classmethod
  def ViewFilterUINames(cls):
    return ('actionable',)

  def __init__(self, *args):
    super().__init__(*args)
    self.not_finalized_viewfilter = ShowNotFinalized(*args)

  def ShowAction(self, an_action):
    containing_context = self.action_to_context(an_action)
    return (self.not_finalized_viewfilter.ShowAction(an_action)
            and (containing_context is None or containing_context.is_active)
            and self.action_to_project(an_action).is_active)

  def ShowProject(self, project):
    return (self.not_finalized_viewfilter.ShowProject(project)
            and project.is_active)

  def ShowFolder(self, a_folder):
    return self.not_finalized_viewfilter.ShowFolder(a_folder)

  def ShowContext(self, context):
    return (self.not_finalized_viewfilter.ShowContext(context)
            and context.is_active)


class ShowNeedingReview(ViewFilter):
  """Shows items that are not deleted, completed, reviewed, or inactive.

  Only Projects need review -- shows Actions in reviewed Projects.
  """

  @classmethod
  def ViewFilterUINames(cls):
    return ('needing_review',)

  def __init__(self, *args):
    super().__init__(*args)
    self.not_finalized_viewfilter = ShowNotFinalized(*args)

  def ShowAction(self, an_action):
    return self.not_finalized_viewfilter.ShowAction(an_action)

  def ShowProject(self, project):
    return (self.not_finalized_viewfilter.ShowProject(project)
            and project.NeedsReview() and project.is_active)

  def ShowFolder(self, a_folder):
    return self.not_finalized_viewfilter.ShowFolder(a_folder)

  def ShowContext(self, context):
    return self.not_finalized_viewfilter.ShowContext(context)


class ShowInactiveIncomplete(ViewFilter):
  """Shows undeleted, incomplete items that are in inactive Projects or Contexts."""

  @classmethod
  def ViewFilterUINames(cls):
    return ('inactive_and_incomplete',)

  def __init__(self, *args):
    super().__init__(*args)
    self.not_finalized_viewfilter = ShowNotFinalized(*args)

  def ShowAction(self, an_action):
    containing_project = self.action_to_project(an_action)
    containing_context = self.action_to_context(an_action)
    return self.not_finalized_viewfilter.ShowAction(an_action) and (
      not containing_project.is_active or (
        containing_context is not None and not containing_context.is_active))

  def ShowProject(self, project):
    return (self.not_finalized_viewfilter.ShowProject(project)
            and (not project.is_active
                 or self.ProjectContainsShownAction(project)))

  def ShowFolder(self, a_folder):
    # TODO(chandler): Show it only if a descendant is inactive and incomplete?
    return self.not_finalized_viewfilter.ShowFolder(a_folder)

  def ShowContext(self, context):
    return self.not_finalized_viewfilter.ShowContext(context) and (
      not context.is_active)


CLS_BY_UI_NAME = {}

_VIEW_FILTER_CLASSES = (
  ShowAll,
  ShowNotDeleted,
  ShowNotFinalized,
  ShowActionable,
  ShowNeedingReview,
  ShowInactiveIncomplete)  # SearchFilter need not be here

for view_filter_cls in _VIEW_FILTER_CLASSES:
  for name in view_filter_cls.ViewFilterUINames():
    assert name not in CLS_BY_UI_NAME, name
    CLS_BY_UI_NAME[name] = view_filter_cls
