// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use serde_json;use crate::incus::EventLifecycleRequestor;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct EventLifecycle {
    pub action: String,

    pub source: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub context: Option<HashMap<String, serde_json::Value>>,

    pub requestor: Option<EventLifecycleRequestor>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub name: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub project: Option<String>,

}