Setup .env

Telemetry retrieve

    tmpy -s 10258 -b 2026-01-01T00:00:00Z -e 2026-03-20T00:00:00Z
    tmpy -s 10265 -b 2026-01-01T00:00:00Z -e 2026-03-20T00:00:00Z
    tmpy -s 10428 -b 2026-01-01T00:00:00Z -e 2026-03-20T00:00:00Z
    tmpy -s 10433 -b 2026-01-01T00:00:00Z -e 2026-03-20T00:00:00Z

Telemetry process

    python ssmm_juice_tm.py -f tm_10433_20260101T000000Z_20260320T000000Z.dds -o sandbox -s

    python ssmm_juice_tm.py -f tm_10258_20260101T000000Z_20260320T000000Z.dds -o sandbox -s
    python ssmm_juice_tm.py -f tm_10265_20260101T000000Z_20260320T000000Z.dds -o sandbox -s
    python ssmm_juice_tm.py -f tm_10428_20260101T000000Z_20260320T000000Z.dds -o sandbox -s