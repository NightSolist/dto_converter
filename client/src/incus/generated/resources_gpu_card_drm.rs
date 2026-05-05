// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesGPUCardDRM {
    pub id: u64,

    pub cardname: String,

    pub carddevice: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub controlname: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub controldevice: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub rendername: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub renderdevice: Option<String>,

}