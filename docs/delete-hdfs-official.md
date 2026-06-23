# DeleteHDFS 2.6.0

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.DeleteHDFS/
Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

DeleteHDFS

### DeleteHDFS

### Description:

Deletes one or more files or directories from HDFS. The path can be provided as an attribute from an incoming FlowFile, or a statically set path that is periodically removed. If this processor has an incoming connection, itwill ignore running on a periodic basis and instead rely on incoming FlowFiles to trigger a delete. Note that you may use a wildcard character to match multiple files or directories. If there are no incoming connections no flowfiles will be transfered to any output relationships. If there is an incoming flowfile then provided there are no detected failures it will be transferred to success otherwise it will be sent to false. If knowledge of globbed files deleted is necessary use ListHDFS first to produce a specific list of files to delete.

### Tags:

hadoop, HCFS, HDFS, delete, remove, filesystem

### Properties:

In the list below, the names of required properties appear in bold. Any other properties (not in bold) are considered optional. The table also indicates any default values, and whether a property supports the NiFi Expression Language.

 | Display Name | API Name | Default Value | Allowable Values | Description

 | Hadoop Configuration Resources | Hadoop Configuration Resources |  |  | A file or comma separated list of files which contains the Hadoop file system configuration. Without this, Hadoop will search the classpath for a 'core-site.xml' and 'hdfs-site.xml' file or will revert to a default configuration. To use swebhdfs, see 'Additional Details' section of PutHDFS's documentation.

This property expects a comma-separated list of file resources.

Supports Expression Language: true (will be evaluated using variable registry only)

 | Kerberos Credentials Service | kerberos-credentials-service |  | Controller Service API:
KerberosCredentialsService
Implementation: KeytabCredentialsService | Specifies the Kerberos Credentials Controller Service that should be used for authenticating with Kerberos

 | Kerberos User Service | kerberos-user-service |  | Controller Service API:
KerberosUserService
Implementations: KerberosPasswordUserService
KerberosKeytabUserService
KerberosTicketCacheUserService | Specifies the Kerberos User Controller Service that should be used for authenticating with Kerberos

 | Kerberos Principal | Kerberos Principal |  |  | Kerberos principal to authenticate as. Requires nifi.kerberos.krb5.file to be set in your nifi.properties
Supports Expression Language: true (will be evaluated using variable registry only)

 | Kerberos Keytab | Kerberos Keytab |  |  | Kerberos keytab associated with the principal. Requires nifi.kerberos.krb5.file to be set in your nifi.properties

This property requires exactly one file to be provided..

Supports Expression Language: true (will be evaluated using variable registry only)

 | Kerberos Password | Kerberos Password |  |  | Kerberos password associated with the principal.
Sensitive Property: true

 | Kerberos Relogin Period | Kerberos Relogin Period | 4 hours |  | Period of time which should pass before attempting a kerberos relogin. This property has been deprecated, and has no effect on processing. Relogins now occur automatically.
Supports Expression Language: true (will be evaluated using variable registry only)

 | Additional Classpath Resources | Additional Classpath Resources |  |  | A comma-separated list of paths to files and/or directories that will be added to the classpath and used for loading native libraries. When specifying a directory, all files with in the directory will be added to the classpath, but further sub-directories will not be included.

This property expects a comma-separated list of resources. Each of the resources may be of any of the following types: file, directory.

 | Path | file_or_directory |  |  | The HDFS file or directory to delete. A wildcard expression may be used to only delete certain files
Supports Expression Language: true (will be evaluated using flow file attributes and variable registry)

 | Recursive | recursive | true |
- true
- false | Remove contents of a non-empty directory recursively

### Relationships:

 | Name | Description

 | success | When an incoming flowfile is used then if there are no errors invoking delete the flowfile will route here.

 | failure | When an incoming flowfile is used and there is a failure while deleting then the flowfile will route here.

### Reads Attributes:
None specified.

### Writes Attributes:

 | Name | Description

 | hdfs.filename | HDFS file to be deleted. If multiple files are deleted, then only the last filename is set.

 | hdfs.path | HDFS Path specified in the delete request. If multiple paths are deleted, then only the last path is set.

 | hadoop.file.url | The hadoop url for the file to be deleted.

 | hdfs.error.message | HDFS error message related to the hdfs.error.code

### State management:
This component does not store state.

### Restricted:

 | Required Permission | Explanation

 | write distributed filesystem | Provides operator the ability to delete any file that NiFi has access to in HDFS or the local filesystem.

### Input requirement:
This component allows an incoming relationship.

### System Resource Considerations:
None specified.

### See Also:

ListHDFS, PutHDFS
