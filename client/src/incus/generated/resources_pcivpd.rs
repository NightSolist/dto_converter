// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesPCIVPD {
    #[serde(skip_serializing_if = "Option::is_none")]    pub productname: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub entries: Option<HashMap<String, String>>,

}