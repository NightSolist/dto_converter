// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeSnapshot {
    pub name: String,

    pub config: ConfigMap,

    pub contenttype: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub description: String,

    pub expiresat: Option<chrono::DateTime<chrono::Utc>>,

}