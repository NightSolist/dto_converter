// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstancePostTarget {
    pub certificate: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub operation: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub websockets: Option<HashMap<String, String>>,

}