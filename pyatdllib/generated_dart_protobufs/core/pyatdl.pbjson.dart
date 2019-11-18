///
//  Generated code. Do not modify.
//  source: core/pyatdl.proto
//
// @dart = 2.3
// ignore_for_file: camel_case_types,non_constant_identifier_names,library_prefixes,unused_import,unused_shown_name,return_of_invalid_type

const VisitorInfo0$json = const {
  '1': 'VisitorInfo0',
  '2': const [
    const {'1': 'sanity_check', '3': 1, '4': 1, '5': 5, '10': 'sanityCheck'},
    const {
      '1': 'cwc_uid',
      '3': 7,
      '4': 1,
      '5': 3,
      '8': const {'6': 1},
      '10': 'cwcUid',
    },
    const {'1': 'view', '3': 3, '4': 1, '5': 9, '10': 'view'},
    const {'1': 'sort', '3': 5, '4': 1, '5': 9, '7': 'alpha', '10': 'sort'},
    const {'1': 'username_hash', '3': 6, '4': 1, '5': 12, '10': 'usernameHash'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const MergeToDoListRequest$json = const {
  '1': 'MergeToDoListRequest',
  '2': const [
    const {'1': 'latest', '3': 16, '4': 1, '5': 11, '6': '.pyatdl.ChecksumAndData', '10': 'latest'},
    const {'1': 'previous_sha1_checksum', '3': 2, '4': 1, '5': 9, '10': 'previousSha1Checksum'},
    const {'1': 'new_data', '3': 3, '4': 1, '5': 8, '7': 'false', '10': 'newData'},
    const {'1': 'overwrite_instead_of_merge', '3': 4, '4': 1, '5': 8, '7': 'false', '10': 'overwriteInsteadOfMerge'},
    const {'1': 'abort_if_merge_is_required', '3': 5, '4': 1, '5': 8, '7': 'false', '10': 'abortIfMergeIsRequired'},
    const {
      '1': 'sanity_check',
      '3': 15,
      '4': 1,
      '5': 6,
      '8': const {'6': 1},
      '10': 'sanityCheck',
    },
  ],
};

const MergeToDoListResponse$json = const {
  '1': 'MergeToDoListResponse',
  '2': const [
    const {'1': 'sha1_checksum', '3': 1, '4': 1, '5': 9, '10': 'sha1Checksum'},
    const {'1': 'to_do_list', '3': 2, '4': 1, '5': 11, '6': '.pyatdl.ToDoList', '10': 'toDoList'},
    const {'1': 'starter_template', '3': 3, '4': 1, '5': 8, '7': 'false', '10': 'starterTemplate'},
    const {
      '1': 'sanity_check',
      '3': 15,
      '4': 1,
      '5': 6,
      '8': const {'6': 1},
      '10': 'sanityCheck',
    },
  ],
};

const ChecksumAndData$json = const {
  '1': 'ChecksumAndData',
  '2': const [
    const {
      '1': 'payload_length',
      '3': 1,
      '4': 2,
      '5': 3,
      '8': const {'6': 1},
      '10': 'payloadLength',
    },
    const {'1': 'sha1_checksum', '3': 2, '4': 1, '5': 9, '10': 'sha1Checksum'},
    const {'1': 'payload_is_zlib_compressed', '3': 3, '4': 1, '5': 8, '10': 'payloadIsZlibCompressed'},
    const {'1': 'payload', '3': 10123, '4': 2, '5': 12, '10': 'payload'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const UserInfoAndToDoList$json = const {
  '1': 'UserInfoAndToDoList',
  '2': const [
    const {'1': 'persona_name', '3': 1, '4': 1, '5': 9, '10': 'personaName'},
    const {'1': 'username', '3': 2, '4': 1, '5': 9, '10': 'username'},
    const {'1': 'json_web_token', '3': 3, '4': 1, '5': 9, '10': 'jsonWebToken'},
    const {'1': 'checksum_and_data', '3': 10123, '4': 1, '5': 11, '6': '.pyatdl.ChecksumAndData', '10': 'checksumAndData'},
  ],
};

const Timestamp$json = const {
  '1': 'Timestamp',
  '2': const [
    const {
      '1': 'ctime',
      '3': 1,
      '4': 1,
      '5': 3,
      '8': const {'6': 1},
      '10': 'ctime',
    },
    const {
      '1': 'dtime',
      '3': 2,
      '4': 1,
      '5': 3,
      '8': const {'6': 1},
      '10': 'dtime',
    },
    const {
      '1': 'mtime',
      '3': 3,
      '4': 1,
      '5': 3,
      '8': const {'6': 1},
      '10': 'mtime',
    },
  ],
};

const Metadata$json = const {
  '1': 'Metadata',
  '2': const [
    const {'1': 'name', '3': 1, '4': 1, '5': 9, '10': 'name'},
    const {'1': 'note', '3': 2, '4': 1, '5': 9, '10': 'note'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const Common$json = const {
  '1': 'Common',
  '2': const [
    const {
      '1': 'uid',
      '3': 4,
      '4': 1,
      '5': 3,
      '8': const {'6': 1},
      '10': 'uid',
    },
    const {'1': 'is_deleted', '3': 1, '4': 1, '5': 8, '10': 'isDeleted'},
    const {'1': 'timestamp', '3': 2, '4': 1, '5': 11, '6': '.pyatdl.Timestamp', '10': 'timestamp'},
    const {'1': 'metadata', '3': 3, '4': 1, '5': 11, '6': '.pyatdl.Metadata', '10': 'metadata'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const Context$json = const {
  '1': 'Context',
  '2': const [
    const {'1': 'common', '3': 1, '4': 1, '5': 11, '6': '.pyatdl.Common', '10': 'common'},
    const {'1': 'is_active', '3': 2, '4': 1, '5': 8, '10': 'isActive'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const Action$json = const {
  '1': 'Action',
  '2': const [
    const {'1': 'common', '3': 1, '4': 1, '5': 11, '6': '.pyatdl.Common', '10': 'common'},
    const {'1': 'is_complete', '3': 3, '4': 1, '5': 8, '10': 'isComplete'},
    const {
      '1': 'ctx_uid',
      '3': 5,
      '4': 1,
      '5': 3,
      '8': const {'6': 1},
      '10': 'ctxUid',
    },
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
  '9': const [
    const {'1': 4, '2': 5},
  ],
};

const Project$json = const {
  '1': 'Project',
  '2': const [
    const {'1': 'common', '3': 1, '4': 1, '5': 11, '6': '.pyatdl.Common', '10': 'common'},
    const {'1': 'is_complete', '3': 2, '4': 1, '5': 8, '10': 'isComplete'},
    const {'1': 'is_active', '3': 3, '4': 1, '5': 8, '10': 'isActive'},
    const {'1': 'actions', '3': 4, '4': 3, '5': 11, '6': '.pyatdl.Action', '10': 'actions'},
    const {'1': 'max_seconds_before_review', '3': 5, '4': 1, '5': 2, '10': 'maxSecondsBeforeReview'},
    const {'1': 'last_review_epoch_seconds', '3': 6, '4': 1, '5': 2, '10': 'lastReviewEpochSeconds'},
    const {
      '1': 'default_context_uid',
      '3': 7,
      '4': 1,
      '5': 3,
      '7': '0',
      '8': const {'6': 1},
      '10': 'defaultContextUid',
    },
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const Note$json = const {
  '1': 'Note',
  '2': const [
    const {'1': 'name', '3': 1, '4': 1, '5': 9, '10': 'name'},
    const {'1': 'note', '3': 2, '4': 1, '5': 9, '10': 'note'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const NoteList$json = const {
  '1': 'NoteList',
  '2': const [
    const {'1': 'notes', '3': 2, '4': 3, '5': 11, '6': '.pyatdl.Note', '10': 'notes'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const ContextList$json = const {
  '1': 'ContextList',
  '2': const [
    const {'1': 'common', '3': 1, '4': 1, '5': 11, '6': '.pyatdl.Common', '10': 'common'},
    const {'1': 'contexts', '3': 2, '4': 3, '5': 11, '6': '.pyatdl.Context', '10': 'contexts'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const Folder$json = const {
  '1': 'Folder',
  '2': const [
    const {'1': 'common', '3': 1, '4': 1, '5': 11, '6': '.pyatdl.Common', '10': 'common'},
    const {'1': 'folders', '3': 2, '4': 3, '5': 11, '6': '.pyatdl.Folder', '10': 'folders'},
    const {'1': 'projects', '3': 3, '4': 3, '5': 11, '6': '.pyatdl.Project', '10': 'projects'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
};

const ToDoList$json = const {
  '1': 'ToDoList',
  '2': const [
    const {'1': 'inbox', '3': 1, '4': 1, '5': 11, '6': '.pyatdl.Project', '10': 'inbox'},
    const {'1': 'root', '3': 2, '4': 1, '5': 11, '6': '.pyatdl.Folder', '10': 'root'},
    const {'1': 'ctx_list', '3': 3, '4': 1, '5': 11, '6': '.pyatdl.ContextList', '10': 'ctxList'},
    const {'1': 'note_list', '3': 5, '4': 1, '5': 11, '6': '.pyatdl.NoteList', '10': 'noteList'},
  ],
  '5': const [
    const {'1': 20000, '2': 536870912},
  ],
  '9': const [
    const {'1': 4, '2': 5},
  ],
};

