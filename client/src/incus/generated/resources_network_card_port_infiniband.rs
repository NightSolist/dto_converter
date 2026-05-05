// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesNetworkCardPortInfiniband {
    #[serde(skip_serializing_if = "Option::is_none")]    pub issmname: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub issmdevice: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub madname: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub maddevice: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub verbname: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub verbdevice: Option<String>,

}