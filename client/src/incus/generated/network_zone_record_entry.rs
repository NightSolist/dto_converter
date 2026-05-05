// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkZoneRecordEntry {
    #[serde(rename = "type")]    pub r#type: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub ttl: Option<u64>,

    pub value: String,

}