"""Defines Prj, our notion of a "project", anything with two or more actions."""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import unicode_literals
from __future__ import print_function

import six
import time

from absl import flags  # type: ignore
from google.protobuf import message
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Type, TypeVar

from . import action
from . import common
from . import container
from . import errors
from . import pyatdl_pb2
from . import uid

FLAGS = flags.FLAGS
DEFAULT_MAX_SECONDS_BEFORE_REVIEW = 3600 * 24 * 7.0


T = TypeVar('T', bound='Prj')


class Prj(container.Container):
  """A project -- anything with two or more actions.

  The implementation allows for zero or one actions, also, but we do
  not suggest that the end user *create* such a project.

  Fields:
    uid: int
    name: None|str|unicode
    note: None|str|unicode
    items: [action.Action]
    max_seconds_before_review: float  # typically one week, 3600 * 24 * 7
    is_complete: bool
    is_deleted: bool
    is_active: bool
    default_context_uid: int|None  # New actions are created in this context

  If you touch a field, you touch this object.  Use copy.deepcopy if
  you do not want to mutate the project.
  """

  __pychecker__ = 'unusednames=cls'

  @classmethod
  def TypesContained(cls) -> Tuple[Type[object]]:
    return (action.Action,)

  # pylint: disable=too-many-arguments
  def __init__(self,
               the_uid: int = None,
               name: str = None,
               items: List[action.Action] = None,
               max_seconds_before_review: float = None,
               is_complete: bool = False,
               is_active: bool = True,
               last_review_epoch_sec: float = 0.0,
               note: str = '',
               default_context_uid: int = None) -> None:
    super().__init__(the_uid=the_uid, items=items, name=name)
    self.note = note
    if max_seconds_before_review is not None:
      self.max_seconds_before_review = max_seconds_before_review
    else:
      self.max_seconds_before_review = DEFAULT_MAX_SECONDS_BEFORE_REVIEW
    self._last_review_epoch_sec = last_review_epoch_sec
    self.is_complete = is_complete
    self.is_active = is_active
    self.default_context_uid = None if default_context_uid == 0 else default_context_uid

  def __unicode__(self) -> str:
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    actions_strs = []
    for a in self.items:
      actions_strs.append(six.text_type(a))
    maxstr = ''
    if self.max_seconds_before_review != DEFAULT_MAX_SECONDS_BEFORE_REVIEW:
      maxstr = ' max_seconds_before_review="%s"' % self.max_seconds_before_review
    return """
<project%s is_deleted="%s" is_complete="%s" is_active="%s"%s name="%s">
%s
</project>
""".strip() % (uid_str, self.is_deleted, self.is_complete, self.is_active,
               maxstr, self.name,
               common.Indented('\n'.join(actions_strs)))

  def __repr__(self) -> str:
    return '<prj_proto>\n%s\n</prj_proto>' % str(self.AsProto())

  def IsDone(self) -> bool:
    return self.is_complete or self.is_deleted

  def AsTaskPaper(self,
                  lines: List[str],
                  context_name: Callable[[int], str] = None,
                  project_name_prefix: str = '',
                  show_action: Callable[[action.Action], bool] = lambda _: True,
                  show_note: Callable[[str], bool] = lambda _: True,
                  hypertext_prefix: str = None,
                  html_escaper: Callable[[str], str] = None) -> None:
    """Appends lines of text to lines.

    Args:
      lines: [unicode]
      context_name: lambda int: unicode  # the integer is a UID
      project_name_prefix: unicode
      show_action: lambda Action: bool
      show_note: lambda str: bool
      hypertext_prefix: None|unicode  # None means to output plain text
      html_escaper: lambda unicode: unicode
    Returns:
      None
    """
    if context_name is None:
      raise TypeError

    # TODO(chandler37): We might want to optionally display @without_context
    # when there is not a context for an action to easily find those actions so
    # you can assign them contexts?
    def Escaped(txt: str) -> str:
      if hypertext_prefix is None:
        return txt
      else:
        if html_escaper is None:
          raise TypeError
        return html_escaper(txt)

    lines.append('')
    full_name = '%s%s:' % (project_name_prefix, self.name)
    if hypertext_prefix is None:
      lines.append(full_name)
    else:
      lines.append('<a href="%s/project/%s">%s%s%s</a>'
                   % (hypertext_prefix, self.uid,
                      '<s>' if self.IsDone() else '',
                      Escaped(full_name),
                      '</s>' if self.IsDone() else ''))
    if self.note and show_note(self.note):
      for line in self.note.replace('\r', '').replace('\\n', ', ').split('\n'):
        lines.append(Escaped(line))
    for item in self.items:
      if not show_action(item):
        continue
      hypernote = ''
      note_suffix = ''
      if item.note and show_note(item.note):
        n = six.text_type(item.note).replace('\r', '').replace('\\n', '\n').strip('\n')
        if hypertext_prefix is None:
          note_suffix = '\tnote: ' + '\t'.join(n.split('\n'))
        else:
          hypernote = '<br>' + '<br>'.join(Escaped(x) for x in n.split('\n'))
      else:
        note_suffix = ''
      if item.ctx_uid is not None:
        cname = context_name(item.ctx_uid).replace(' ', '_')
        context_suffix = ' %s' % (cname,) if cname.startswith('@') else ' @%s' % (cname,)
        if context_suffix.strip() in item.name:
          context_suffix = ''
      else:
        context_suffix = ''
      if item.is_complete:
        done_suffix = ' @done'
      else:
        done_suffix = ''
      if item.is_deleted:
        deleted_suffix = ' @deleted'
        done_suffix = ' @done'
      else:
        deleted_suffix = ''
      action_text = '%s%s%s%s%s' % (item.name, note_suffix, context_suffix,
                                    done_suffix, deleted_suffix)
      if hypertext_prefix is None:
        lines.append('\t- %s' % action_text)
      else:
        lines.append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                     '- <a href="%s/action/%s">%s%s%s%s</a>'
                     % (hypertext_prefix, item.uid,
                        '<s>' if item.is_complete or item.is_deleted else '',
                        Escaped(action_text),
                        hypernote,
                        '</s>' if item.is_complete or item.is_deleted else ''))

  def MarkAsNeedingReview(self) -> None:
    """Clears the reviewed status, if reviewed."""
    self._last_review_epoch_sec = 0.0

  def MarkAsReviewed(self, when: float = None) -> None:
    """Note that the end user has reviewed this project.  By default, when is now.

    Args:
      when: float  # seconds since the epoch
    """
    self._last_review_epoch_sec = time.time() if when is None else when

  def TimeOfLastReview(self) -> float:
    """Returns a float, seconds since the epoch, or zero if this
    project has never been reviewed.
    """
    return self._last_review_epoch_sec

  def NeedsReview(self, now: float = None) -> bool:
    """Returns true iff the project needs review.

    Args:
      now: float  # seconds since the epoch
    Returns:
      bool
    """
    if now is None:
      now = time.time()
    cutoff = now - self.max_seconds_before_review
    return self.TimeOfLastReview() < cutoff

  def Projects(self) -> Iterator[Tuple[Prj, List[container.Container]]]:
    """Override."""
    yield (self, [])

  def AsProto(self, pb: message.Message = None) -> pyatdl_pb2.Project:
    # pylint: disable=maybe-no-member
    if pb is None:
      pb = pyatdl_pb2.Project()
    if not isinstance(pb, pyatdl_pb2.Project):
      raise TypeError
    super().AsProto(pb.common)
    if self.note:
      pb.common.metadata.note = self.note
    pb.is_complete = self.is_complete
    pb.is_active = self.is_active
    if self.default_context_uid is not None:
      pb.default_context_uid = self.default_context_uid
    if abs(self.max_seconds_before_review - DEFAULT_MAX_SECONDS_BEFORE_REVIEW) > 1e-6:
      pb.max_seconds_before_review = self.max_seconds_before_review
    if self._last_review_epoch_sec:
      pb.last_review_epoch_seconds = self._last_review_epoch_sec
    for a in self.items:
      pba = pb.actions.add()
      a.AsProto(pba)
    return pb

  def MergeFromProto(self,
                     other: pyatdl_pb2.Project,
                     *,
                     mtimes_by_uid_in_remote_to_do_list: Dict[int, float],
                     find_existing_action_by_uid: Callable[[int], Optional[Tuple[action.Action, Prj]]]) -> None:
    """Add things in other but not in self (anywhere, not just self) to self.

    Change things in self to match what are in other for existing things (judged by UID) that are more recent according
    to max(ctime,mtime,dtime).

    (TODO(chandler): Make the flutter app (a client of the mergeprotobufs API) look at max(ctime,mtime,dtime) to
    determine a floor for its timestamps.)
    """
    if not isinstance(other, pyatdl_pb2.Project):
      raise TypeError
    if common.MaxTimeOfPb(other) > common.MaxTime(self):
      self.__dict__['default_context_uid'] = None if other.default_context_uid == 0 else other.default_context_uid
      self.__dict__['is_complete'] = other.is_complete
      self.__dict__['is_active'] = other.is_active
      self.__dict__['last_review_epoch_sec'] = other.last_review_epoch_seconds
      self.__dict__['max_seconds_before_review'] = (
        other.max_seconds_before_review if other.HasField('max_seconds_before_review') else DEFAULT_MAX_SECONDS_BEFORE_REVIEW)
      self.MergeCommonFrom(other)
    uids_to_delete = set()
    for ii in self.items:
      remote_mtime = mtimes_by_uid_in_remote_to_do_list.get(ii.uid, float('-inf'))
      # we should only delete if we're going to make the move, and the move depends on the mtime (TODO(DLC): not mtime but
      # MaxTime):
      if ii.mtime <= remote_mtime:
        uids_to_delete.add(ii.uid)
    if uids_to_delete:
      # No, do not self.NoteModification() because the mtime of the project proper should not have to do with the
      # actions contained. 'self.items =' would trigger __setattr__ which triggers NoteModification:
      self.items[:] = [i for i in self.items if i.uid not in uids_to_delete]
    for other_action in other.actions:
      if other_action.common.uid in (uid.DEFAULT_PROTOBUF_VALUE_FOR_ABSENT_UID, uid.ROOT_FOLDER_UID, uid.INBOX_UID):
        raise AssertionError("merge error: illegal or missing UID")  # TODO(chandler37): do this in more places, too
      tup = find_existing_action_by_uid(other_action.common.uid)
      if tup is None:
        # You might wonder, what if this used to exist here and the most recent thing we did was purge it? You are not
        # supposed to purge without syncing 100% of devices.
        self.items.append(
          action.Action.DeserializedProtobuf(
            other_action.SerializeToString()))
      else:
        existing_action, existing_project = tup
        they_are_authority = common.MaxTimeOfPb(other_action) >= common.MaxTime(existing_action)
        if they_are_authority:
          existing_action.MergeFromProto(other_action)
          if existing_project.uid != self.uid:
            self.items.append(existing_action)
            existing_project.DeleteItemByUid(other_action.common.uid)

  @classmethod
  def DeserializedProtobuf(cls: Type[T], bytestring) -> T:
    """Deserializes a Prj from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      Prj
    Raises:
      errors.DataError
    """
    if not bytestring:
      raise errors.DataError("empty project in the protocol buffer -- not even a UID is present")
    pb = pyatdl_pb2.Project.FromString(bytestring)  # pylint: disable=no-member
    if pb.HasField('max_seconds_before_review'):
      max_seconds_before_review = pb.max_seconds_before_review
    else:
      max_seconds_before_review = DEFAULT_MAX_SECONDS_BEFORE_REVIEW
    p = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            note=pb.common.metadata.note,
            is_complete=pb.is_complete,
            is_active=pb.is_active,
            default_context_uid=pb.default_context_uid,
            max_seconds_before_review=max_seconds_before_review,
            last_review_epoch_sec=pb.last_review_epoch_seconds)
    for pb_action in pb.actions:
      p.items.append(action.Action.DeserializedProtobuf(
        pb_action.SerializeToString()))
    p.SetFieldsBasedOnProtobuf(pb.common)  # must be last
    return p
