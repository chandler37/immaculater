///
//  Generated code. Do not modify.
//  source: core/pyatdl.proto
//
// @dart = 2.7
// ignore_for_file: annotate_overrides,camel_case_types,unnecessary_const,non_constant_identifier_names,library_prefixes,unused_import,unused_shown_name,return_of_invalid_type,unnecessary_this,prefer_final_fields

import 'dart:core' as $core;

import 'package:fixnum/fixnum.dart' as $fixnum;
import 'package:protobuf/protobuf.dart' as $pb;

class VisitorInfo0 extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'VisitorInfo0', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..a<$core.int>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'sanityCheck', $pb.PbFieldType.O3)
    ..aOS(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'view')
    ..a<$core.String>(5, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'sort', $pb.PbFieldType.OS, defaultOrMaker: 'alpha')
    ..a<$core.List<$core.int>>(6, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'usernameHash', $pb.PbFieldType.OY)
    ..aInt64(7, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'cwcUid')
    ..hasExtensions = true
  ;

  VisitorInfo0._() : super();
  factory VisitorInfo0({
    $core.int sanityCheck,
    $core.String view,
    $core.String sort,
    $core.List<$core.int> usernameHash,
    $fixnum.Int64 cwcUid,
  }) {
    final _result = create();
    if (sanityCheck != null) {
      _result.sanityCheck = sanityCheck;
    }
    if (view != null) {
      _result.view = view;
    }
    if (sort != null) {
      _result.sort = sort;
    }
    if (usernameHash != null) {
      _result.usernameHash = usernameHash;
    }
    if (cwcUid != null) {
      _result.cwcUid = cwcUid;
    }
    return _result;
  }
  factory VisitorInfo0.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory VisitorInfo0.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  VisitorInfo0 clone() => VisitorInfo0()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  VisitorInfo0 copyWith(void Function(VisitorInfo0) updates) => super.copyWith((message) => updates(message as VisitorInfo0)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static VisitorInfo0 create() => VisitorInfo0._();
  VisitorInfo0 createEmptyInstance() => create();
  static $pb.PbList<VisitorInfo0> createRepeated() => $pb.PbList<VisitorInfo0>();
  @$core.pragma('dart2js:noInline')
  static VisitorInfo0 getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<VisitorInfo0>(create);
  static VisitorInfo0 _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get sanityCheck => $_getIZ(0);
  @$pb.TagNumber(1)
  set sanityCheck($core.int v) { $_setSignedInt32(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasSanityCheck() => $_has(0);
  @$pb.TagNumber(1)
  void clearSanityCheck() => clearField(1);

  @$pb.TagNumber(3)
  $core.String get view => $_getSZ(1);
  @$pb.TagNumber(3)
  set view($core.String v) { $_setString(1, v); }
  @$pb.TagNumber(3)
  $core.bool hasView() => $_has(1);
  @$pb.TagNumber(3)
  void clearView() => clearField(3);

  @$pb.TagNumber(5)
  $core.String get sort => $_getS(2, 'alpha');
  @$pb.TagNumber(5)
  set sort($core.String v) { $_setString(2, v); }
  @$pb.TagNumber(5)
  $core.bool hasSort() => $_has(2);
  @$pb.TagNumber(5)
  void clearSort() => clearField(5);

  @$pb.TagNumber(6)
  $core.List<$core.int> get usernameHash => $_getN(3);
  @$pb.TagNumber(6)
  set usernameHash($core.List<$core.int> v) { $_setBytes(3, v); }
  @$pb.TagNumber(6)
  $core.bool hasUsernameHash() => $_has(3);
  @$pb.TagNumber(6)
  void clearUsernameHash() => clearField(6);

  @$pb.TagNumber(7)
  $fixnum.Int64 get cwcUid => $_getI64(4);
  @$pb.TagNumber(7)
  set cwcUid($fixnum.Int64 v) { $_setInt64(4, v); }
  @$pb.TagNumber(7)
  $core.bool hasCwcUid() => $_has(4);
  @$pb.TagNumber(7)
  void clearCwcUid() => clearField(7);
}

class MergeToDoListRequest extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'MergeToDoListRequest', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOS(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'previousSha1Checksum')
    ..aOB(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'newData')
    ..aOB(4, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'overwriteInsteadOfMerge')
    ..aOB(5, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'abortIfMergeIsRequired')
    ..a<$fixnum.Int64>(15, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'sanityCheck', $pb.PbFieldType.OF6, defaultOrMaker: $fixnum.Int64.ZERO)
    ..aOM<ChecksumAndData>(16, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'latest', subBuilder: ChecksumAndData.create)
  ;

  MergeToDoListRequest._() : super();
  factory MergeToDoListRequest({
    $core.String previousSha1Checksum,
    $core.bool newData,
    $core.bool overwriteInsteadOfMerge,
    $core.bool abortIfMergeIsRequired,
    $fixnum.Int64 sanityCheck,
    ChecksumAndData latest,
  }) {
    final _result = create();
    if (previousSha1Checksum != null) {
      _result.previousSha1Checksum = previousSha1Checksum;
    }
    if (newData != null) {
      _result.newData = newData;
    }
    if (overwriteInsteadOfMerge != null) {
      _result.overwriteInsteadOfMerge = overwriteInsteadOfMerge;
    }
    if (abortIfMergeIsRequired != null) {
      _result.abortIfMergeIsRequired = abortIfMergeIsRequired;
    }
    if (sanityCheck != null) {
      _result.sanityCheck = sanityCheck;
    }
    if (latest != null) {
      _result.latest = latest;
    }
    return _result;
  }
  factory MergeToDoListRequest.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory MergeToDoListRequest.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  MergeToDoListRequest clone() => MergeToDoListRequest()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  MergeToDoListRequest copyWith(void Function(MergeToDoListRequest) updates) => super.copyWith((message) => updates(message as MergeToDoListRequest)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static MergeToDoListRequest create() => MergeToDoListRequest._();
  MergeToDoListRequest createEmptyInstance() => create();
  static $pb.PbList<MergeToDoListRequest> createRepeated() => $pb.PbList<MergeToDoListRequest>();
  @$core.pragma('dart2js:noInline')
  static MergeToDoListRequest getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<MergeToDoListRequest>(create);
  static MergeToDoListRequest _defaultInstance;

  @$pb.TagNumber(2)
  $core.String get previousSha1Checksum => $_getSZ(0);
  @$pb.TagNumber(2)
  set previousSha1Checksum($core.String v) { $_setString(0, v); }
  @$pb.TagNumber(2)
  $core.bool hasPreviousSha1Checksum() => $_has(0);
  @$pb.TagNumber(2)
  void clearPreviousSha1Checksum() => clearField(2);

  @$pb.TagNumber(3)
  $core.bool get newData => $_getBF(1);
  @$pb.TagNumber(3)
  set newData($core.bool v) { $_setBool(1, v); }
  @$pb.TagNumber(3)
  $core.bool hasNewData() => $_has(1);
  @$pb.TagNumber(3)
  void clearNewData() => clearField(3);

  @$pb.TagNumber(4)
  $core.bool get overwriteInsteadOfMerge => $_getBF(2);
  @$pb.TagNumber(4)
  set overwriteInsteadOfMerge($core.bool v) { $_setBool(2, v); }
  @$pb.TagNumber(4)
  $core.bool hasOverwriteInsteadOfMerge() => $_has(2);
  @$pb.TagNumber(4)
  void clearOverwriteInsteadOfMerge() => clearField(4);

  @$pb.TagNumber(5)
  $core.bool get abortIfMergeIsRequired => $_getBF(3);
  @$pb.TagNumber(5)
  set abortIfMergeIsRequired($core.bool v) { $_setBool(3, v); }
  @$pb.TagNumber(5)
  $core.bool hasAbortIfMergeIsRequired() => $_has(3);
  @$pb.TagNumber(5)
  void clearAbortIfMergeIsRequired() => clearField(5);

  @$pb.TagNumber(15)
  $fixnum.Int64 get sanityCheck => $_getI64(4);
  @$pb.TagNumber(15)
  set sanityCheck($fixnum.Int64 v) { $_setInt64(4, v); }
  @$pb.TagNumber(15)
  $core.bool hasSanityCheck() => $_has(4);
  @$pb.TagNumber(15)
  void clearSanityCheck() => clearField(15);

  @$pb.TagNumber(16)
  ChecksumAndData get latest => $_getN(5);
  @$pb.TagNumber(16)
  set latest(ChecksumAndData v) { setField(16, v); }
  @$pb.TagNumber(16)
  $core.bool hasLatest() => $_has(5);
  @$pb.TagNumber(16)
  void clearLatest() => clearField(16);
  @$pb.TagNumber(16)
  ChecksumAndData ensureLatest() => $_ensure(5);
}

class MergeToDoListResponse extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'MergeToDoListResponse', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOS(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'sha1Checksum')
    ..aOM<ToDoList>(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'toDoList', subBuilder: ToDoList.create)
    ..aOB(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'starterTemplate')
    ..a<$fixnum.Int64>(15, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'sanityCheck', $pb.PbFieldType.OF6, defaultOrMaker: $fixnum.Int64.ZERO)
  ;

  MergeToDoListResponse._() : super();
  factory MergeToDoListResponse({
    $core.String sha1Checksum,
    ToDoList toDoList,
    $core.bool starterTemplate,
    $fixnum.Int64 sanityCheck,
  }) {
    final _result = create();
    if (sha1Checksum != null) {
      _result.sha1Checksum = sha1Checksum;
    }
    if (toDoList != null) {
      _result.toDoList = toDoList;
    }
    if (starterTemplate != null) {
      _result.starterTemplate = starterTemplate;
    }
    if (sanityCheck != null) {
      _result.sanityCheck = sanityCheck;
    }
    return _result;
  }
  factory MergeToDoListResponse.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory MergeToDoListResponse.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  MergeToDoListResponse clone() => MergeToDoListResponse()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  MergeToDoListResponse copyWith(void Function(MergeToDoListResponse) updates) => super.copyWith((message) => updates(message as MergeToDoListResponse)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static MergeToDoListResponse create() => MergeToDoListResponse._();
  MergeToDoListResponse createEmptyInstance() => create();
  static $pb.PbList<MergeToDoListResponse> createRepeated() => $pb.PbList<MergeToDoListResponse>();
  @$core.pragma('dart2js:noInline')
  static MergeToDoListResponse getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<MergeToDoListResponse>(create);
  static MergeToDoListResponse _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get sha1Checksum => $_getSZ(0);
  @$pb.TagNumber(1)
  set sha1Checksum($core.String v) { $_setString(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasSha1Checksum() => $_has(0);
  @$pb.TagNumber(1)
  void clearSha1Checksum() => clearField(1);

  @$pb.TagNumber(2)
  ToDoList get toDoList => $_getN(1);
  @$pb.TagNumber(2)
  set toDoList(ToDoList v) { setField(2, v); }
  @$pb.TagNumber(2)
  $core.bool hasToDoList() => $_has(1);
  @$pb.TagNumber(2)
  void clearToDoList() => clearField(2);
  @$pb.TagNumber(2)
  ToDoList ensureToDoList() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.bool get starterTemplate => $_getBF(2);
  @$pb.TagNumber(3)
  set starterTemplate($core.bool v) { $_setBool(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasStarterTemplate() => $_has(2);
  @$pb.TagNumber(3)
  void clearStarterTemplate() => clearField(3);

  @$pb.TagNumber(15)
  $fixnum.Int64 get sanityCheck => $_getI64(3);
  @$pb.TagNumber(15)
  set sanityCheck($fixnum.Int64 v) { $_setInt64(3, v); }
  @$pb.TagNumber(15)
  $core.bool hasSanityCheck() => $_has(3);
  @$pb.TagNumber(15)
  void clearSanityCheck() => clearField(15);
}

class ChecksumAndData extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'ChecksumAndData', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..a<$fixnum.Int64>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'payloadLength', $pb.PbFieldType.Q6, defaultOrMaker: $fixnum.Int64.ZERO)
    ..aOS(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'sha1Checksum')
    ..aOB(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'payloadIsZlibCompressed')
    ..a<$core.List<$core.int>>(10123, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'payload', $pb.PbFieldType.QY)
    ..hasExtensions = true
  ;

  ChecksumAndData._() : super();
  factory ChecksumAndData({
    $fixnum.Int64 payloadLength,
    $core.String sha1Checksum,
    $core.bool payloadIsZlibCompressed,
    $core.List<$core.int> payload,
  }) {
    final _result = create();
    if (payloadLength != null) {
      _result.payloadLength = payloadLength;
    }
    if (sha1Checksum != null) {
      _result.sha1Checksum = sha1Checksum;
    }
    if (payloadIsZlibCompressed != null) {
      _result.payloadIsZlibCompressed = payloadIsZlibCompressed;
    }
    if (payload != null) {
      _result.payload = payload;
    }
    return _result;
  }
  factory ChecksumAndData.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory ChecksumAndData.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  ChecksumAndData clone() => ChecksumAndData()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  ChecksumAndData copyWith(void Function(ChecksumAndData) updates) => super.copyWith((message) => updates(message as ChecksumAndData)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static ChecksumAndData create() => ChecksumAndData._();
  ChecksumAndData createEmptyInstance() => create();
  static $pb.PbList<ChecksumAndData> createRepeated() => $pb.PbList<ChecksumAndData>();
  @$core.pragma('dart2js:noInline')
  static ChecksumAndData getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<ChecksumAndData>(create);
  static ChecksumAndData _defaultInstance;

  @$pb.TagNumber(1)
  $fixnum.Int64 get payloadLength => $_getI64(0);
  @$pb.TagNumber(1)
  set payloadLength($fixnum.Int64 v) { $_setInt64(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasPayloadLength() => $_has(0);
  @$pb.TagNumber(1)
  void clearPayloadLength() => clearField(1);

  @$pb.TagNumber(2)
  $core.String get sha1Checksum => $_getSZ(1);
  @$pb.TagNumber(2)
  set sha1Checksum($core.String v) { $_setString(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasSha1Checksum() => $_has(1);
  @$pb.TagNumber(2)
  void clearSha1Checksum() => clearField(2);

  @$pb.TagNumber(3)
  $core.bool get payloadIsZlibCompressed => $_getBF(2);
  @$pb.TagNumber(3)
  set payloadIsZlibCompressed($core.bool v) { $_setBool(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasPayloadIsZlibCompressed() => $_has(2);
  @$pb.TagNumber(3)
  void clearPayloadIsZlibCompressed() => clearField(3);

  @$pb.TagNumber(10123)
  $core.List<$core.int> get payload => $_getN(3);
  @$pb.TagNumber(10123)
  set payload($core.List<$core.int> v) { $_setBytes(3, v); }
  @$pb.TagNumber(10123)
  $core.bool hasPayload() => $_has(3);
  @$pb.TagNumber(10123)
  void clearPayload() => clearField(10123);
}

class UserInfoAndToDoList extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'UserInfoAndToDoList', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOS(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'personaName')
    ..aOS(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'username')
    ..aOS(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'jsonWebToken')
    ..aOM<ChecksumAndData>(10123, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'checksumAndData', subBuilder: ChecksumAndData.create)
  ;

  UserInfoAndToDoList._() : super();
  factory UserInfoAndToDoList({
    $core.String personaName,
    $core.String username,
    $core.String jsonWebToken,
    ChecksumAndData checksumAndData,
  }) {
    final _result = create();
    if (personaName != null) {
      _result.personaName = personaName;
    }
    if (username != null) {
      _result.username = username;
    }
    if (jsonWebToken != null) {
      _result.jsonWebToken = jsonWebToken;
    }
    if (checksumAndData != null) {
      _result.checksumAndData = checksumAndData;
    }
    return _result;
  }
  factory UserInfoAndToDoList.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory UserInfoAndToDoList.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  UserInfoAndToDoList clone() => UserInfoAndToDoList()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  UserInfoAndToDoList copyWith(void Function(UserInfoAndToDoList) updates) => super.copyWith((message) => updates(message as UserInfoAndToDoList)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static UserInfoAndToDoList create() => UserInfoAndToDoList._();
  UserInfoAndToDoList createEmptyInstance() => create();
  static $pb.PbList<UserInfoAndToDoList> createRepeated() => $pb.PbList<UserInfoAndToDoList>();
  @$core.pragma('dart2js:noInline')
  static UserInfoAndToDoList getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<UserInfoAndToDoList>(create);
  static UserInfoAndToDoList _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get personaName => $_getSZ(0);
  @$pb.TagNumber(1)
  set personaName($core.String v) { $_setString(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasPersonaName() => $_has(0);
  @$pb.TagNumber(1)
  void clearPersonaName() => clearField(1);

  @$pb.TagNumber(2)
  $core.String get username => $_getSZ(1);
  @$pb.TagNumber(2)
  set username($core.String v) { $_setString(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasUsername() => $_has(1);
  @$pb.TagNumber(2)
  void clearUsername() => clearField(2);

  @$pb.TagNumber(3)
  $core.String get jsonWebToken => $_getSZ(2);
  @$pb.TagNumber(3)
  set jsonWebToken($core.String v) { $_setString(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasJsonWebToken() => $_has(2);
  @$pb.TagNumber(3)
  void clearJsonWebToken() => clearField(3);

  @$pb.TagNumber(10123)
  ChecksumAndData get checksumAndData => $_getN(3);
  @$pb.TagNumber(10123)
  set checksumAndData(ChecksumAndData v) { setField(10123, v); }
  @$pb.TagNumber(10123)
  $core.bool hasChecksumAndData() => $_has(3);
  @$pb.TagNumber(10123)
  void clearChecksumAndData() => clearField(10123);
  @$pb.TagNumber(10123)
  ChecksumAndData ensureChecksumAndData() => $_ensure(3);
}

class Timestamp extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Timestamp', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aInt64(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'ctime')
    ..aInt64(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'dtime')
    ..aInt64(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'mtime')
    ..hasRequiredFields = false
  ;

  Timestamp._() : super();
  factory Timestamp({
    $fixnum.Int64 ctime,
    $fixnum.Int64 dtime,
    $fixnum.Int64 mtime,
  }) {
    final _result = create();
    if (ctime != null) {
      _result.ctime = ctime;
    }
    if (dtime != null) {
      _result.dtime = dtime;
    }
    if (mtime != null) {
      _result.mtime = mtime;
    }
    return _result;
  }
  factory Timestamp.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Timestamp.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Timestamp clone() => Timestamp()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Timestamp copyWith(void Function(Timestamp) updates) => super.copyWith((message) => updates(message as Timestamp)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Timestamp create() => Timestamp._();
  Timestamp createEmptyInstance() => create();
  static $pb.PbList<Timestamp> createRepeated() => $pb.PbList<Timestamp>();
  @$core.pragma('dart2js:noInline')
  static Timestamp getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Timestamp>(create);
  static Timestamp _defaultInstance;

  @$pb.TagNumber(1)
  $fixnum.Int64 get ctime => $_getI64(0);
  @$pb.TagNumber(1)
  set ctime($fixnum.Int64 v) { $_setInt64(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasCtime() => $_has(0);
  @$pb.TagNumber(1)
  void clearCtime() => clearField(1);

  @$pb.TagNumber(2)
  $fixnum.Int64 get dtime => $_getI64(1);
  @$pb.TagNumber(2)
  set dtime($fixnum.Int64 v) { $_setInt64(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasDtime() => $_has(1);
  @$pb.TagNumber(2)
  void clearDtime() => clearField(2);

  @$pb.TagNumber(3)
  $fixnum.Int64 get mtime => $_getI64(2);
  @$pb.TagNumber(3)
  set mtime($fixnum.Int64 v) { $_setInt64(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasMtime() => $_has(2);
  @$pb.TagNumber(3)
  void clearMtime() => clearField(3);
}

class Metadata extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Metadata', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOS(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'name')
    ..aOS(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'note')
    ..hasExtensions = true
  ;

  Metadata._() : super();
  factory Metadata({
    $core.String name,
    $core.String note,
  }) {
    final _result = create();
    if (name != null) {
      _result.name = name;
    }
    if (note != null) {
      _result.note = note;
    }
    return _result;
  }
  factory Metadata.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Metadata.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Metadata clone() => Metadata()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Metadata copyWith(void Function(Metadata) updates) => super.copyWith((message) => updates(message as Metadata)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Metadata create() => Metadata._();
  Metadata createEmptyInstance() => create();
  static $pb.PbList<Metadata> createRepeated() => $pb.PbList<Metadata>();
  @$core.pragma('dart2js:noInline')
  static Metadata getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Metadata>(create);
  static Metadata _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get name => $_getSZ(0);
  @$pb.TagNumber(1)
  set name($core.String v) { $_setString(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasName() => $_has(0);
  @$pb.TagNumber(1)
  void clearName() => clearField(1);

  @$pb.TagNumber(2)
  $core.String get note => $_getSZ(1);
  @$pb.TagNumber(2)
  set note($core.String v) { $_setString(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasNote() => $_has(1);
  @$pb.TagNumber(2)
  void clearNote() => clearField(2);
}

class Common extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Common', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOB(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'isDeleted')
    ..aOM<Timestamp>(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'timestamp', subBuilder: Timestamp.create)
    ..aOM<Metadata>(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'metadata', subBuilder: Metadata.create)
    ..aInt64(4, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'uid')
    ..hasExtensions = true
  ;

  Common._() : super();
  factory Common({
    $core.bool isDeleted,
    Timestamp timestamp,
    Metadata metadata,
    $fixnum.Int64 uid,
  }) {
    final _result = create();
    if (isDeleted != null) {
      _result.isDeleted = isDeleted;
    }
    if (timestamp != null) {
      _result.timestamp = timestamp;
    }
    if (metadata != null) {
      _result.metadata = metadata;
    }
    if (uid != null) {
      _result.uid = uid;
    }
    return _result;
  }
  factory Common.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Common.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Common clone() => Common()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Common copyWith(void Function(Common) updates) => super.copyWith((message) => updates(message as Common)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Common create() => Common._();
  Common createEmptyInstance() => create();
  static $pb.PbList<Common> createRepeated() => $pb.PbList<Common>();
  @$core.pragma('dart2js:noInline')
  static Common getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Common>(create);
  static Common _defaultInstance;

  @$pb.TagNumber(1)
  $core.bool get isDeleted => $_getBF(0);
  @$pb.TagNumber(1)
  set isDeleted($core.bool v) { $_setBool(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasIsDeleted() => $_has(0);
  @$pb.TagNumber(1)
  void clearIsDeleted() => clearField(1);

  @$pb.TagNumber(2)
  Timestamp get timestamp => $_getN(1);
  @$pb.TagNumber(2)
  set timestamp(Timestamp v) { setField(2, v); }
  @$pb.TagNumber(2)
  $core.bool hasTimestamp() => $_has(1);
  @$pb.TagNumber(2)
  void clearTimestamp() => clearField(2);
  @$pb.TagNumber(2)
  Timestamp ensureTimestamp() => $_ensure(1);

  @$pb.TagNumber(3)
  Metadata get metadata => $_getN(2);
  @$pb.TagNumber(3)
  set metadata(Metadata v) { setField(3, v); }
  @$pb.TagNumber(3)
  $core.bool hasMetadata() => $_has(2);
  @$pb.TagNumber(3)
  void clearMetadata() => clearField(3);
  @$pb.TagNumber(3)
  Metadata ensureMetadata() => $_ensure(2);

  @$pb.TagNumber(4)
  $fixnum.Int64 get uid => $_getI64(3);
  @$pb.TagNumber(4)
  set uid($fixnum.Int64 v) { $_setInt64(3, v); }
  @$pb.TagNumber(4)
  $core.bool hasUid() => $_has(3);
  @$pb.TagNumber(4)
  void clearUid() => clearField(4);
}

class Context extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Context', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOM<Common>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'common', subBuilder: Common.create)
    ..aOB(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'isActive')
    ..hasExtensions = true
  ;

  Context._() : super();
  factory Context({
    Common common,
    $core.bool isActive,
  }) {
    final _result = create();
    if (common != null) {
      _result.common = common;
    }
    if (isActive != null) {
      _result.isActive = isActive;
    }
    return _result;
  }
  factory Context.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Context.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Context clone() => Context()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Context copyWith(void Function(Context) updates) => super.copyWith((message) => updates(message as Context)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Context create() => Context._();
  Context createEmptyInstance() => create();
  static $pb.PbList<Context> createRepeated() => $pb.PbList<Context>();
  @$core.pragma('dart2js:noInline')
  static Context getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Context>(create);
  static Context _defaultInstance;

  @$pb.TagNumber(1)
  Common get common => $_getN(0);
  @$pb.TagNumber(1)
  set common(Common v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasCommon() => $_has(0);
  @$pb.TagNumber(1)
  void clearCommon() => clearField(1);
  @$pb.TagNumber(1)
  Common ensureCommon() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.bool get isActive => $_getBF(1);
  @$pb.TagNumber(2)
  set isActive($core.bool v) { $_setBool(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasIsActive() => $_has(1);
  @$pb.TagNumber(2)
  void clearIsActive() => clearField(2);
}

class Action extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Action', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOM<Common>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'common', subBuilder: Common.create)
    ..aOB(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'isComplete')
    ..aInt64(5, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'ctxUid')
    ..hasExtensions = true
  ;

  Action._() : super();
  factory Action({
    Common common,
    $core.bool isComplete,
    $fixnum.Int64 ctxUid,
  }) {
    final _result = create();
    if (common != null) {
      _result.common = common;
    }
    if (isComplete != null) {
      _result.isComplete = isComplete;
    }
    if (ctxUid != null) {
      _result.ctxUid = ctxUid;
    }
    return _result;
  }
  factory Action.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Action.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Action clone() => Action()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Action copyWith(void Function(Action) updates) => super.copyWith((message) => updates(message as Action)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Action create() => Action._();
  Action createEmptyInstance() => create();
  static $pb.PbList<Action> createRepeated() => $pb.PbList<Action>();
  @$core.pragma('dart2js:noInline')
  static Action getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Action>(create);
  static Action _defaultInstance;

  @$pb.TagNumber(1)
  Common get common => $_getN(0);
  @$pb.TagNumber(1)
  set common(Common v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasCommon() => $_has(0);
  @$pb.TagNumber(1)
  void clearCommon() => clearField(1);
  @$pb.TagNumber(1)
  Common ensureCommon() => $_ensure(0);

  @$pb.TagNumber(3)
  $core.bool get isComplete => $_getBF(1);
  @$pb.TagNumber(3)
  set isComplete($core.bool v) { $_setBool(1, v); }
  @$pb.TagNumber(3)
  $core.bool hasIsComplete() => $_has(1);
  @$pb.TagNumber(3)
  void clearIsComplete() => clearField(3);

  @$pb.TagNumber(5)
  $fixnum.Int64 get ctxUid => $_getI64(2);
  @$pb.TagNumber(5)
  set ctxUid($fixnum.Int64 v) { $_setInt64(2, v); }
  @$pb.TagNumber(5)
  $core.bool hasCtxUid() => $_has(2);
  @$pb.TagNumber(5)
  void clearCtxUid() => clearField(5);
}

class Project extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Project', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOM<Common>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'common', subBuilder: Common.create)
    ..aOB(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'isComplete')
    ..aOB(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'isActive')
    ..pc<Action>(4, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'actions', $pb.PbFieldType.PM, subBuilder: Action.create)
    ..a<$core.double>(5, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'maxSecondsBeforeReview', $pb.PbFieldType.OF)
    ..a<$core.double>(6, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'lastReviewEpochSeconds', $pb.PbFieldType.OF)
    ..aInt64(7, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'defaultContextUid')
    ..hasExtensions = true
  ;

  Project._() : super();
  factory Project({
    Common common,
    $core.bool isComplete,
    $core.bool isActive,
    $core.Iterable<Action> actions,
    $core.double maxSecondsBeforeReview,
    $core.double lastReviewEpochSeconds,
    $fixnum.Int64 defaultContextUid,
  }) {
    final _result = create();
    if (common != null) {
      _result.common = common;
    }
    if (isComplete != null) {
      _result.isComplete = isComplete;
    }
    if (isActive != null) {
      _result.isActive = isActive;
    }
    if (actions != null) {
      _result.actions.addAll(actions);
    }
    if (maxSecondsBeforeReview != null) {
      _result.maxSecondsBeforeReview = maxSecondsBeforeReview;
    }
    if (lastReviewEpochSeconds != null) {
      _result.lastReviewEpochSeconds = lastReviewEpochSeconds;
    }
    if (defaultContextUid != null) {
      _result.defaultContextUid = defaultContextUid;
    }
    return _result;
  }
  factory Project.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Project.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Project clone() => Project()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Project copyWith(void Function(Project) updates) => super.copyWith((message) => updates(message as Project)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Project create() => Project._();
  Project createEmptyInstance() => create();
  static $pb.PbList<Project> createRepeated() => $pb.PbList<Project>();
  @$core.pragma('dart2js:noInline')
  static Project getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Project>(create);
  static Project _defaultInstance;

  @$pb.TagNumber(1)
  Common get common => $_getN(0);
  @$pb.TagNumber(1)
  set common(Common v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasCommon() => $_has(0);
  @$pb.TagNumber(1)
  void clearCommon() => clearField(1);
  @$pb.TagNumber(1)
  Common ensureCommon() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.bool get isComplete => $_getBF(1);
  @$pb.TagNumber(2)
  set isComplete($core.bool v) { $_setBool(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasIsComplete() => $_has(1);
  @$pb.TagNumber(2)
  void clearIsComplete() => clearField(2);

  @$pb.TagNumber(3)
  $core.bool get isActive => $_getBF(2);
  @$pb.TagNumber(3)
  set isActive($core.bool v) { $_setBool(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasIsActive() => $_has(2);
  @$pb.TagNumber(3)
  void clearIsActive() => clearField(3);

  @$pb.TagNumber(4)
  $core.List<Action> get actions => $_getList(3);

  @$pb.TagNumber(5)
  $core.double get maxSecondsBeforeReview => $_getN(4);
  @$pb.TagNumber(5)
  set maxSecondsBeforeReview($core.double v) { $_setFloat(4, v); }
  @$pb.TagNumber(5)
  $core.bool hasMaxSecondsBeforeReview() => $_has(4);
  @$pb.TagNumber(5)
  void clearMaxSecondsBeforeReview() => clearField(5);

  @$pb.TagNumber(6)
  $core.double get lastReviewEpochSeconds => $_getN(5);
  @$pb.TagNumber(6)
  set lastReviewEpochSeconds($core.double v) { $_setFloat(5, v); }
  @$pb.TagNumber(6)
  $core.bool hasLastReviewEpochSeconds() => $_has(5);
  @$pb.TagNumber(6)
  void clearLastReviewEpochSeconds() => clearField(6);

  @$pb.TagNumber(7)
  $fixnum.Int64 get defaultContextUid => $_getI64(6);
  @$pb.TagNumber(7)
  set defaultContextUid($fixnum.Int64 v) { $_setInt64(6, v); }
  @$pb.TagNumber(7)
  $core.bool hasDefaultContextUid() => $_has(6);
  @$pb.TagNumber(7)
  void clearDefaultContextUid() => clearField(7);
}

class Note extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Note', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOS(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'name')
    ..aOS(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'note')
    ..hasExtensions = true
  ;

  Note._() : super();
  factory Note({
    $core.String name,
    $core.String note,
  }) {
    final _result = create();
    if (name != null) {
      _result.name = name;
    }
    if (note != null) {
      _result.note = note;
    }
    return _result;
  }
  factory Note.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Note.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Note clone() => Note()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Note copyWith(void Function(Note) updates) => super.copyWith((message) => updates(message as Note)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Note create() => Note._();
  Note createEmptyInstance() => create();
  static $pb.PbList<Note> createRepeated() => $pb.PbList<Note>();
  @$core.pragma('dart2js:noInline')
  static Note getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Note>(create);
  static Note _defaultInstance;

  @$pb.TagNumber(1)
  $core.String get name => $_getSZ(0);
  @$pb.TagNumber(1)
  set name($core.String v) { $_setString(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasName() => $_has(0);
  @$pb.TagNumber(1)
  void clearName() => clearField(1);

  @$pb.TagNumber(2)
  $core.String get note => $_getSZ(1);
  @$pb.TagNumber(2)
  set note($core.String v) { $_setString(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasNote() => $_has(1);
  @$pb.TagNumber(2)
  void clearNote() => clearField(2);
}

class NoteList extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'NoteList', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..pc<Note>(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'notes', $pb.PbFieldType.PM, subBuilder: Note.create)
    ..hasExtensions = true
  ;

  NoteList._() : super();
  factory NoteList({
    $core.Iterable<Note> notes,
  }) {
    final _result = create();
    if (notes != null) {
      _result.notes.addAll(notes);
    }
    return _result;
  }
  factory NoteList.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory NoteList.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  NoteList clone() => NoteList()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  NoteList copyWith(void Function(NoteList) updates) => super.copyWith((message) => updates(message as NoteList)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static NoteList create() => NoteList._();
  NoteList createEmptyInstance() => create();
  static $pb.PbList<NoteList> createRepeated() => $pb.PbList<NoteList>();
  @$core.pragma('dart2js:noInline')
  static NoteList getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<NoteList>(create);
  static NoteList _defaultInstance;

  @$pb.TagNumber(2)
  $core.List<Note> get notes => $_getList(0);
}

class ContextList extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'ContextList', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..pc<Context>(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'contexts', $pb.PbFieldType.PM, subBuilder: Context.create)
    ..hasExtensions = true
  ;

  ContextList._() : super();
  factory ContextList({
    $core.Iterable<Context> contexts,
  }) {
    final _result = create();
    if (contexts != null) {
      _result.contexts.addAll(contexts);
    }
    return _result;
  }
  factory ContextList.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory ContextList.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  ContextList clone() => ContextList()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  ContextList copyWith(void Function(ContextList) updates) => super.copyWith((message) => updates(message as ContextList)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static ContextList create() => ContextList._();
  ContextList createEmptyInstance() => create();
  static $pb.PbList<ContextList> createRepeated() => $pb.PbList<ContextList>();
  @$core.pragma('dart2js:noInline')
  static ContextList getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<ContextList>(create);
  static ContextList _defaultInstance;

  @$pb.TagNumber(2)
  $core.List<Context> get contexts => $_getList(0);
}

class Folder extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'Folder', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOM<Common>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'common', subBuilder: Common.create)
    ..pc<Folder>(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'folders', $pb.PbFieldType.PM, subBuilder: Folder.create)
    ..pc<Project>(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'projects', $pb.PbFieldType.PM, subBuilder: Project.create)
    ..hasExtensions = true
  ;

  Folder._() : super();
  factory Folder({
    Common common,
    $core.Iterable<Folder> folders,
    $core.Iterable<Project> projects,
  }) {
    final _result = create();
    if (common != null) {
      _result.common = common;
    }
    if (folders != null) {
      _result.folders.addAll(folders);
    }
    if (projects != null) {
      _result.projects.addAll(projects);
    }
    return _result;
  }
  factory Folder.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Folder.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  Folder clone() => Folder()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  Folder copyWith(void Function(Folder) updates) => super.copyWith((message) => updates(message as Folder)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Folder create() => Folder._();
  Folder createEmptyInstance() => create();
  static $pb.PbList<Folder> createRepeated() => $pb.PbList<Folder>();
  @$core.pragma('dart2js:noInline')
  static Folder getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Folder>(create);
  static Folder _defaultInstance;

  @$pb.TagNumber(1)
  Common get common => $_getN(0);
  @$pb.TagNumber(1)
  set common(Common v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasCommon() => $_has(0);
  @$pb.TagNumber(1)
  void clearCommon() => clearField(1);
  @$pb.TagNumber(1)
  Common ensureCommon() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.List<Folder> get folders => $_getList(1);

  @$pb.TagNumber(3)
  $core.List<Project> get projects => $_getList(2);
}

class ToDoList extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'ToDoList', package: const $pb.PackageName(const $core.bool.fromEnvironment('protobuf.omit_message_names') ? '' : 'pyatdl'), createEmptyInstance: create)
    ..aOM<Project>(1, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'inbox', subBuilder: Project.create)
    ..aOM<Folder>(2, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'root', subBuilder: Folder.create)
    ..aOM<ContextList>(3, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'ctxList', subBuilder: ContextList.create)
    ..aOM<NoteList>(5, const $core.bool.fromEnvironment('protobuf.omit_field_names') ? '' : 'noteList', subBuilder: NoteList.create)
    ..hasExtensions = true
  ;

  ToDoList._() : super();
  factory ToDoList({
    Project inbox,
    Folder root,
    ContextList ctxList,
    NoteList noteList,
  }) {
    final _result = create();
    if (inbox != null) {
      _result.inbox = inbox;
    }
    if (root != null) {
      _result.root = root;
    }
    if (ctxList != null) {
      _result.ctxList = ctxList;
    }
    if (noteList != null) {
      _result.noteList = noteList;
    }
    return _result;
  }
  factory ToDoList.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory ToDoList.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.deepCopy] instead. '
  'Will be removed in next major version')
  ToDoList clone() => ToDoList()..mergeFromMessage(this);
  @$core.Deprecated(
  'Using this can add significant overhead to your binary. '
  'Use [GeneratedMessageGenericExtensions.rebuild] instead. '
  'Will be removed in next major version')
  ToDoList copyWith(void Function(ToDoList) updates) => super.copyWith((message) => updates(message as ToDoList)); // ignore: deprecated_member_use
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static ToDoList create() => ToDoList._();
  ToDoList createEmptyInstance() => create();
  static $pb.PbList<ToDoList> createRepeated() => $pb.PbList<ToDoList>();
  @$core.pragma('dart2js:noInline')
  static ToDoList getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<ToDoList>(create);
  static ToDoList _defaultInstance;

  @$pb.TagNumber(1)
  Project get inbox => $_getN(0);
  @$pb.TagNumber(1)
  set inbox(Project v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasInbox() => $_has(0);
  @$pb.TagNumber(1)
  void clearInbox() => clearField(1);
  @$pb.TagNumber(1)
  Project ensureInbox() => $_ensure(0);

  @$pb.TagNumber(2)
  Folder get root => $_getN(1);
  @$pb.TagNumber(2)
  set root(Folder v) { setField(2, v); }
  @$pb.TagNumber(2)
  $core.bool hasRoot() => $_has(1);
  @$pb.TagNumber(2)
  void clearRoot() => clearField(2);
  @$pb.TagNumber(2)
  Folder ensureRoot() => $_ensure(1);

  @$pb.TagNumber(3)
  ContextList get ctxList => $_getN(2);
  @$pb.TagNumber(3)
  set ctxList(ContextList v) { setField(3, v); }
  @$pb.TagNumber(3)
  $core.bool hasCtxList() => $_has(2);
  @$pb.TagNumber(3)
  void clearCtxList() => clearField(3);
  @$pb.TagNumber(3)
  ContextList ensureCtxList() => $_ensure(2);

  @$pb.TagNumber(5)
  NoteList get noteList => $_getN(3);
  @$pb.TagNumber(5)
  set noteList(NoteList v) { setField(5, v); }
  @$pb.TagNumber(5)
  $core.bool hasNoteList() => $_has(3);
  @$pb.TagNumber(5)
  void clearNoteList() => clearField(5);
  @$pb.TagNumber(5)
  NoteList ensureNoteList() => $_ensure(3);
}

