# Cookbook: Common Tasks

This page contains real-world examples and patterns for using dictutils in your projects.

:::{tip}
💡 **Found a bug or have suggestions?** [Open an issue](https://github.com/adieyal/dictutils/issues) on GitHub!
:::

## Data Analysis

### Build nested dict from query results (qsdict)

```python
from dictutils import qsdict
import json

# Sales data by region and product
sales = [
    {"region": "North", "product": "Widget", "revenue": 1000, "units": 50},
    {"region": "North", "product": "Gadget", "revenue": 1500, "units": 30},
    {"region": "South", "product": "Widget", "revenue": 800, "units": 40},
    {"region": "South", "product": "Gadget", "revenue": 1200, "units": 25},
]

# Group by region -> product, show revenue
result = qsdict(sales, "region", "product", "revenue")
print(json.dumps(result, indent=4))
# Output:
# {
#     "North": {
#         "Gadget": 1500,
#         "Widget": 1000
#     },
#     "South": {
#         "Gadget": 1200,
#         "Widget": 800
#     }
# }

# Group by region, show multiple values as tuple
result = qsdict(sales, "region", ("revenue", "units"))
print(json.dumps(result, indent=4))
# Output:
# {
#     "North": [1000, 50, 1500, 30],
#     "South": [800, 40, 1200, 25]
# }
```

### Aggregate data by groups (nest_agg)

```python
from dictutils import nest_agg, Agg
import json

# Survey responses
responses = [
    {"department": "Engineering", "satisfaction": 8, "salary": 95000},
    {"department": "Engineering", "satisfaction": 9, "salary": 105000}, 
    {"department": "Marketing", "satisfaction": 7, "salary": 75000},
    {"department": "Marketing", "satisfaction": 6, "salary": 80000},
]

# Calculate average satisfaction and salary by department
aggs = {
    "avg_satisfaction": Agg(
        map=lambda x: x["satisfaction"],
        zero=0,
        reduce=lambda a, b: a + b,
        finalize=lambda total: total / 2  # Simplified for demo
    ),
    "avg_salary": Agg(
        map=lambda x: (x["salary"], 1),
        zero=(0, 0),
        reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        finalize=lambda x: x[0] / x[1] if x[1] > 0 else 0
    )
}

result = nest_agg(responses, keys=["department"], aggs=aggs)
print(json.dumps(result, indent=4))
# Output:
# {
#     "Engineering": {
#         "avg_salary": 100000.0,
#         "avg_satisfaction": 8.5
#     },
#     "Marketing": {
#         "avg_salary": 77500.0,
#         "avg_satisfaction": 6.5
#     }
# }
```

### Pivot data structure (pivot)

```python
from dictutils import pivot
import json

# Time series data: month -> metric -> value
monthly_metrics = {
    "Jan": {"revenue": 10000, "users": 500, "conversion": 0.05},
    "Feb": {"revenue": 12000, "users": 600, "conversion": 0.06},
    "Mar": {"revenue": 11000, "users": 550, "conversion": 0.055}
}

# Pivot to: metric -> month -> value
result = pivot(monthly_metrics, [1, 0])
print(json.dumps(result, indent=4))
# Output:
# {
#     "conversion": {
#         "Feb": 0.06,
#         "Jan": 0.05,
#         "Mar": 0.055
#     },
#     "revenue": {
#         "Feb": 12000,
#         "Jan": 10000,
#         "Mar": 11000
#     },
#     "users": {
#         "Feb": 600,
#         "Jan": 500,
#         "Mar": 550
#     }
# }
```

### Deduplicate by id

```python
from dictutils.ops import distinct_by
import json

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}, 
    {"id": 1, "name": "Alice Updated", "email": "alice.new@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
]

result = distinct_by(users, key="id")
print(json.dumps(result, indent=4))
# Output:
# [
#     {
#         "id": 1,
#         "name": "Alice",
#         "email": "alice@example.com"
#     },
#     {
#         "id": 2,
#         "name": "Bob",
#         "email": "bob@example.com"
#     },
#     {
#         "id": 3,
#         "name": "Charlie",
#         "email": "charlie@example.com"
#     }
# ]
```

## Configuration Management

### Deep merge configurations (mergedict)

```python
from dictutils import mergedict
import json

# Environment-specific configurations
base_config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "options": {"timeout": 30, "pool_size": 10}
    },
    "features": {
        "analytics": True,
        "debugging": False
    }
}

prod_config = {
    "database": {
        "host": "prod.db.example.com",
        "options": {"pool_size": 50, "ssl": True}
    },
    "features": {
        "debugging": False,
        "monitoring": True
    }
}

# Merge configurations (prod overrides base)
result = mergedict(base_config, prod_config)
print(json.dumps(result, indent=4))
# Output:
# {
#     "database": {
#         "host": "prod.db.example.com",
#         "options": {
#             "pool_size": 50,
#             "ssl": true,
#             "timeout": 30
#         },
#         "port": 5432
#     },
#     "features": {
#         "analytics": true,
#         "debugging": false,
#         "monitoring": true
#     }
# }
```

### Merge but keep first value

```python
from dictutils.ops import deep_update
import json

# Feature flags with defaults vs user overrides
defaults = {"feature_a": True, "feature_b": False, "timeout": 30}
user_prefs = {"feature_a": False, "feature_c": True, "timeout": 60}

result = deep_update(defaults, user_prefs, scalar_strategy="keep_first")
print(json.dumps(result, indent=4))
# Output:
# {
#     "feature_a": true,
#     "feature_b": false,
#     "feature_c": true,
#     "timeout": 30
# }
```

### Remove empty/None values

```python
from dictutils.ops import prune
import json

# Clean up configuration with empty values
config = {
    "api_key": "abc123",
    "debug_mode": None,
    "endpoints": [],
    "database": {
        "host": "localhost",
        "password": None,
        "options": {}
    },
    "features": {
        "cache": True,
        "logging": None
    }
}

result = prune(config)
print(json.dumps(result, indent=4))
# Output:
# {
#     "api_key": "abc123",
#     "database": {
#         "host": "localhost"
#     },
#     "features": {
#         "cache": true
#     }
# }
```

## Data Integration

### Flatten to dot paths and back

```python
from dictutils.ops import flatten_paths, expand_paths
import json

# API response with nested structure
api_response = {
    "user": {
        "profile": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    },
    "metadata": {
        "created_at": "2023-01-01",
        "version": "1.0"
    }
}

# Flatten for easier processing/storage
flat = flatten_paths(api_response)
print(json.dumps(flat, indent=4))
# Output:
# {
#     "metadata.created_at": "2023-01-01",
#     "metadata.version": "1.0",
#     "user.profile.email": "john@example.com",
#     "user.profile.name": "John Doe",
#     "user.settings.notifications": true,
#     "user.settings.theme": "dark"
# }

# Reconstruct original structure
restored = expand_paths(flat)
print(json.dumps(restored, indent=4))
# Output: (same as original api_response)
```

### Normalize API responses

```python
from dictutils import qsdict
from dictutils.ops import deep_update
import json

# Different API formats for the same data
api1_users = [
    {"id": 1, "full_name": "Alice Smith", "contact": {"email": "alice@example.com"}},
    {"id": 2, "full_name": "Bob Jones", "contact": {"email": "bob@example.com"}}
]

api2_users = [
    {"user_id": 1, "name": "Alice Smith", "email_address": "alice@api2.com"},
    {"user_id": 3, "name": "Charlie Brown", "email_address": "charlie@api2.com"}
]

# Normalize to common format
def normalize_api1(user):
    return {
        "id": user["id"],
        "name": user["full_name"],
        "email": user["contact"]["email"],
        "source": "api1"
    }

def normalize_api2(user):
    return {
        "id": user["user_id"],
        "name": user["name"], 
        "email": user["email_address"],
        "source": "api2"
    }

normalized = [normalize_api1(u) for u in api1_users] + [normalize_api2(u) for u in api2_users]
print(json.dumps(normalized, indent=4))
# Output:
# [
#     {
#         "id": 1,
#         "name": "Alice Smith",
#         "email": "alice@example.com",
#         "source": "api1"
#     },
#     {
#         "id": 2,
#         "name": "Bob Jones",
#         "email": "bob@example.com",
#         "source": "api1"
#     },
#     {
#         "id": 1,
#         "name": "Alice Smith",
#         "email": "alice@api2.com",
#         "source": "api2"
#     },
#     {
#         "id": 3,
#         "name": "Charlie Brown",
#         "email": "charlie@api2.com",
#         "source": "api2"
#     }
# ]

# Build lookup by ID
user_lookup = qsdict(normalized, "id", "source", lambda u: {"name": u["name"], "email": u["email"]})
print(json.dumps(user_lookup, indent=4))
# Output:
# {
#     "1": {
#         "api1": {
#             "name": "Alice Smith",
#             "email": "alice@example.com"
#         },
#         "api2": {
#             "name": "Alice Smith",
#             "email": "alice@api2.com"
#         }
#     },
#     "2": {
#         "api1": {
#             "name": "Bob Jones",
#             "email": "bob@example.com"
#         }
#     },
#     "3": {
#         "api2": {
#             "name": "Charlie Brown",
#             "email": "charlie@api2.com"
#         }
#     }
# }
```
