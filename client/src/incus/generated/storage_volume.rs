// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolume {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub usedby: Vec<String>,

    pub location: String,

    pub contenttype: String,

    pub project: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub config: ConfigMap,

    pub description: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub restore: Option<String>,

}