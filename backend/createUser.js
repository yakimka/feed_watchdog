db.createUser({
    user: "feed_watchdog",
    pwd: "ba61bcb7-73ae-4b8c-a1c2-7e5e2959a9b1",
    roles: [
        {
            role: "readWrite",
            db: "feed_watchdog"
        }
    ]
});
