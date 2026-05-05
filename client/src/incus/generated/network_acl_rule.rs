// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkACLRule {
    pub action: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub source: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub destination: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub protocol: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub sourceport: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub destinationport: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub icmptype: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub icmpcode: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub description: Option<String>,

    pub state: String,

}