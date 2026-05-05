// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceSnapshot {
    pub architecture: String,

    pub config: ConfigMap,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub description: String,

    pub devices: DevicesMap,

    pub ephemeral: bool,

    #[serde(skip_serializing_if = "Option::is_none")]    pub expandedconfig: Option<ConfigMap>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub expandeddevices: Option<DevicesMap>,

    pub lastusedat: chrono::DateTime<chrono::Utc>,

    pub name: String,

    pub profiles: Vec<String>,

    pub stateful: bool,

    pub size: i64,

    pub expiresat: chrono::DateTime<chrono::Utc>,

}