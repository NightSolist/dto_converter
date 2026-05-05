// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::StorageVolumeBackup;
use crate::incus::StorageVolumeSnapshot;
use crate::incus::StorageVolumeState;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeFull {
    pub backups: Vec<StorageVolumeBackup>,

    pub snapshots: Vec<StorageVolumeSnapshot>,

    pub state: Option<StorageVolumeState>,

    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub usedby: Vec<String>,

    pub location: String,

    pub contenttype: String,

    pub project: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

}