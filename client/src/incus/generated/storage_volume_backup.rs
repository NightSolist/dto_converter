// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeBackup {
    pub name: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub volumeonly: bool,

    pub optimizedstorage: bool,

}