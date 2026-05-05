// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::BackupTarget;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeBackupsPost {
    pub name: String,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub volumeonly: bool,

    pub optimizedstorage: bool,

    pub compressionalgorithm: String,

    pub target: Option<BackupTarget>,

}