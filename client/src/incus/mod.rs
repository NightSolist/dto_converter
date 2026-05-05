pub mod custom;
pub mod generated;

// Переэкспортируем всё наружу, чтобы клиент мог импортировать типы напрямую
pub use custom::*;
pub use generated::*;