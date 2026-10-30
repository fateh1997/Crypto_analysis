"""Entry point: runs fetch -> metrics -> rules -> report end to end.

Thin on purpose: report.write_report() already does the full pipeline.
This file exists just to give the project one obvious, explicitly
named command to run.
"""

from report import write_report

if __name__ == "__main__":
    write_report()
