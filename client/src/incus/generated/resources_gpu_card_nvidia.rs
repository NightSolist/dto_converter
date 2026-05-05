// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesGPUCardNvidia {
    #[serde(skip_serializing_if = "Option::is_none")]    pub cudaversion: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub nvrmversion: Option<String>,

    pub brand: String,

    pub model: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub uuid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub architecture: Option<String>,

    pub cardname: String,

    pub carddevice: String,

}