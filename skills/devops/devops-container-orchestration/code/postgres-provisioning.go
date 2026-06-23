// PostgreSQL 資料庫配置範例
package main

import (
    "database/sql"
    "net/url"
)

func provisionDatabase(adminDSN, dbName, username, password string) error {
    // 1. Connect to admin database
    adminDB, err := sql.Open("postgres", adminDSN)
    if err != nil {
        return err
    }
    defer adminDB.Close()

    // 2. Create database and user
    _, err = adminDB.Exec("CREATE USER " + username + " WITH PASSWORD '" + password + "'")
    if err != nil {
        return err
    }
    
    _, err = adminDB.Exec("CREATE DATABASE " + dbName + " OWNER " + username)
    if err != nil {
        return err
    }

    // 3. Connect to NEW database for extensions
    parsedDSN, err := url.Parse(adminDSN)
    if err != nil {
        return err
    }
    parsedDSN.Path = "/" + dbName
    
    userDB, err := sql.Open("postgres", parsedDSN.String())
    if err != nil {
        return err
    }
    defer userDB.Close()

    // 4. Install extensions and grant permissions
    _, err = userDB.Exec("GRANT ALL ON SCHEMA public TO " + username)
    if err != nil {
        return err
    }
    
    _, err = userDB.Exec("CREATE EXTENSION IF NOT EXISTS vector")
    return err
}
