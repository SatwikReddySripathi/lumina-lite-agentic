import pandas as pd
from typing import Dict, List, Any
from langchain_core.tools import tool


@tool
def query_employee_database(
    filter_criteria: Dict[str, str] = None,
    columns: List[str] = None
) -> Dict[str, Any]:
    """
    Query the HR employee database (CSV).
    
    Args:
        filter_criteria: Dict of column: value pairs to filter by
            Examples: 
            - {"department": "Digital Workplace AI"}
            - {"role": "Data Scientist", "location": "Boston"}
            - {"full_name": "Sarah Chen"}
        columns: List of columns to return (None = all columns)
            Available: employee_id, full_name, role, department, 
                      location, office, start_date, manager, email
    
    Returns:
        {
            "employees": List of matching employee records,
            "count": Number of matches,
            "columns": List of column names returned
        }
    """
    df = pd.read_csv("data/employees.csv")
    
    if filter_criteria:
        for col, value in filter_criteria.items():
            if col in df.columns:
                df = df[df[col].str.contains(value, case=False, na=False)]
    
    if columns:
        available_cols = [c for c in columns if c in df.columns]
        df = df[available_cols]
    
    employees = df.to_dict('records')
    
    return {
        "employees": employees,
        "count": len(employees),
        "columns": list(df.columns)
    }


@tool
def get_employee_by_name(name: str) -> Dict[str, Any]:
    """
    Look up a specific employee by name (partial match supported).
    
    Args:
        name: Full or partial name to search for
    
    Returns:
        Employee record with all details, or None if not found
    """
    df = pd.read_csv("data/employees.csv")
    
    matches = df[df['full_name'].str.contains(name, case=False, na=False)]
    
    if len(matches) == 0:
        return {
            "found": False,
            "message": f"No employee found matching '{name}'"
        }
    
    if len(matches) == 1:
        return {
            "found": True,
            "employee": matches.iloc[0].to_dict()
        }
    
    return {
        "found": True,
        "multiple_matches": True,
        "count": len(matches),
        "employees": matches.to_dict('records')
    }


@tool
def get_team_members(department: str = None, manager: str = None) -> Dict[str, Any]:
    """
    Get all members of a team or department.
    
    Args:
        department: Department name (partial match)
        manager: Manager name (partial match)
    
    Returns:
        List of team members with their details
    """
    df = pd.read_csv("data/employees.csv")
    
    if department:
        df = df[df['department'].str.contains(department, case=False, na=False)]
    
    if manager:
        df = df[df['manager'].str.contains(manager, case=False, na=False)]
    
    if len(df) == 0:
        return {
            "found": False,
            "message": "No team members found matching criteria"
        }
    
    return {
        "found": True,
        "count": len(df),
        "team_members": df.to_dict('records'),
        "roles": df['role'].unique().tolist(),
        "locations": df['location'].unique().tolist()
    }


@tool
def get_location_summary(location: str = None) -> Dict[str, Any]:
    """
    Get summary of employees by location.
    
    Args:
        location: Optional location filter (e.g., "Boston", "Remote")
    
    Returns:
        Summary statistics by location
    """
    df = pd.read_csv("data/employees.csv")
    
    if location:
        df = df[df['location'].str.contains(location, case=False, na=False)]
    
    summary = df.groupby(['location', 'role']).size().reset_index(name='count')
    
    return {
        "total_employees": len(df),
        "locations": df['location'].value_counts().to_dict(),
        "by_location_and_role": summary.to_dict('records'),
        "departments": df['department'].value_counts().to_dict()
    }