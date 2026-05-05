// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Default)]
pub enum ResponseType {
    #[default]    #[serde(rename = "sync")]    SyncResponse,
    #[serde(rename = "async")]    AsyncResponse,
    #[serde(rename = "error")]    ErrorResponse,
}