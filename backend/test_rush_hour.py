from rush_hour import classify_rush_hours, format_windows

# two separate congested windows, like the idea.md example (8-10am, 4-7pm)
ratios = [
    (6, 1.0), (7, 1.05),
    (8, 1.3), (9, 1.25),
    (10, 1.0), (11, 1.0), (12, 1.0), (13, 1.0), (14, 1.0), (15, 1.05),
    (16, 1.4), (17, 1.5), (18, 1.35),
    (19, 1.0), (20, 1.0),
]

windows = classify_rush_hours(ratios, threshold=1.15)
assert windows == [(8, 10), (16, 19)], windows
assert format_windows(windows) == "Peak traffic 8am-10am, 4pm-7pm"

assert classify_rush_hours([(6, 1.0), (7, 1.0)]) == []
assert format_windows([]) == "No significant rush hour congestion detected."

# congestion running to the end of the sampled range should still close out
assert classify_rush_hours([(20, 1.3), (21, 1.4)]) == [(20, 22)]

print("all tests passed")
