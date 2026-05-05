// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeSnapshotPut {
    pub description: String,

    pub expiresat: Option<chrono::DateTime<chrono::Utc>>,

}