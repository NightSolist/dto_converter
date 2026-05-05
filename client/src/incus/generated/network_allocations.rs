// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkAllocations {
    pub address: String,

    pub hwaddr: String,

    pub nat: bool,

    #[serde(rename = "type")]    pub r#type: String,

    pub usedby: String,

}