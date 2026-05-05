// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::StorageBucketBackup;
use crate::incus::StorageBucketKey;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageBucketFull {
    pub backups: Vec<StorageBucketBackup>,

    pub keys: Vec<StorageBucketKey>,

    pub name: String,

    pub s3url: String,

    pub location: String,

    pub project: String,

}