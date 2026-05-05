// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageBucketBackupsPost {
    pub name: String,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub compressionalgorithm: String,

}