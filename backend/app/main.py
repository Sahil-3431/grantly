from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import sqlite3, os

DB_PATH = os.getenv('DATABASE_PATH', str(Path(__file__).resolve().parent.parent / 'grantly.db'))
app = FastAPI(title='GRANTLY API', version='1.0.0', description='Scholarship discovery and application tracking API')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173').split(','), allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def db():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn

def init_db():
    con=db(); cur=con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS scholarships (id INTEGER PRIMARY KEY, name TEXT NOT NULL, provider TEXT NOT NULL, amount TEXT, deadline TEXT, level TEXT, category TEXT, location TEXT, eligibility TEXT, description TEXT, documents TEXT, source TEXT, official_url TEXT, updated_at TEXT DEFAULT CURRENT_DATE)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, scholarship_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'Interested', applied_date TEXT, notes TEXT DEFAULT '', UNIQUE(student_id, scholarship_id))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS saved_scholarships (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, scholarship_id INTEGER NOT NULL, UNIQUE(student_id, scholarship_id))''')
    count=cur.execute('SELECT COUNT(*) FROM scholarships').fetchone()[0]
    if count==0:
        rows=[(1,'National Means-cum-Merit Scholarship','Ministry of Education, Government of India','₹12,000 / year','2026-12-15','Class 9–12','School','India','Students studying in Class 9 with at least 55% marks in Class 8. Family income should be within official scheme limits.','A centrally sponsored scholarship to support meritorious students from economically weaker sections.','Previous year marksheet|Income certificate|School verification|Bank passbook|Aadhaar / ID proof','National Scholarship Portal','https://scholarships.gov.in'),(2,'Post Matric Scholarship for Minorities','Ministry of Minority Affairs','Up to ₹10,000','2026-11-30','Class 11–Postgraduate','Post-matric','India','Students belonging to notified minority communities, with at least 50% marks and family income within scheme limits.','Financial assistance for students from notified minority communities pursuing studies after Class 10.','Previous marksheet|Income certificate|Community certificate|Bank details|Fee receipt','National Scholarship Portal','https://scholarships.gov.in'),(3,'AICTE Pragati Scholarship','All India Council for Technical Education','₹50,000 / year','2027-01-10','Undergraduate','Technical','India','Girl students admitted to the first year of an AICTE-approved technical degree or diploma programme. Subject to annual family income criteria.','Support for girl students pursuing technical education in AICTE-approved institutions.','Admission letter|Family income certificate|Class 10 & 12 marksheets|Aadhaar|Bank passbook','AICTE','https://www.aicte-india.org'),(4,'Central Sector Scheme of Scholarship','Department of Higher Education','₹12,000–₹20,000','2026-12-20','Undergraduate','Merit-based','India','Students above the 80th percentile in the relevant Class 12 board examination and meeting the notified income criteria.','Merit-based financial support for college and university students.','Class 12 marksheet|Income certificate|College ID|Bank details','National Scholarship Portal','https://scholarships.gov.in')]
        cur.executemany('INSERT INTO scholarships(id,name,provider,amount,deadline,level,category,location,eligibility,description,documents,source,official_url) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',rows)
    con.commit(); con.close()
init_db()

class ApplicationIn(BaseModel):
    student_id: str = 'demo-student'
    scholarship_id: int
    status: str = 'Interested'
    applied_date: str | None = None
    notes: str = ''
class StatusIn(BaseModel):
    status: str = Field(pattern='^(Interested|Preparing|Applied|Under Review|Approved|Rejected)$')
    notes: str | None = None
class SaveIn(BaseModel):
    student_id: str = 'demo-student'
    scholarship_id: int
class ChatIn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

@app.get('/')
def root(): return {'name':'GRANTLY API','status':'ok','docs':'/docs'}
@app.get('/health')
def health(): return {'status':'healthy'}
@app.get('/api/scholarships')
def list_scholarships(q: str = '', category: str = 'All'):
    con=db(); rows=con.execute('SELECT * FROM scholarships WHERE (lower(name) LIKE ? OR lower(provider) LIKE ? OR lower(category) LIKE ?) AND (?="All" OR category=?) ORDER BY deadline', (f'%{q.lower()}%',f'%{q.lower()}%',f'%{q.lower()}%',category,category)).fetchall(); con.close()
    return [dict(r, documents=r['documents'].split('|')) for r in rows]
@app.get('/api/scholarships/{scholarship_id}')
def get_scholarship(scholarship_id:int):
    con=db(); row=con.execute('SELECT * FROM scholarships WHERE id=?',(scholarship_id,)).fetchone(); con.close()
    if not row: raise HTTPException(404,'Scholarship not found')
    return dict(row,documents=row['documents'].split('|'))
@app.post('/api/saved')
def save_scholarship(data:SaveIn):
    con=db()
    if not con.execute('SELECT id FROM scholarships WHERE id=?',(data.scholarship_id,)).fetchone(): con.close(); raise HTTPException(404,'Scholarship not found')
    con.execute('INSERT OR IGNORE INTO saved_scholarships(student_id,scholarship_id) VALUES(?,?)',(data.student_id,data.scholarship_id)); con.commit(); con.close(); return {'saved':True}
@app.delete('/api/saved/{scholarship_id}')
def unsave_scholarship(scholarship_id:int, student_id:str='demo-student'):
    con=db(); con.execute('DELETE FROM saved_scholarships WHERE student_id=? AND scholarship_id=?',(student_id,scholarship_id)); con.commit(); con.close(); return {'saved':False}
@app.get('/api/saved')
def get_saved(student_id:str='demo-student'):
    con=db(); rows=con.execute('SELECT s.* FROM scholarships s JOIN saved_scholarships b ON b.scholarship_id=s.id WHERE b.student_id=?',(student_id,)).fetchall(); con.close(); return [dict(r,documents=r['documents'].split('|')) for r in rows]
@app.post('/api/applications')
def add_application(data:ApplicationIn):
    con=db()
    if not con.execute('SELECT id FROM scholarships WHERE id=?',(data.scholarship_id,)).fetchone(): con.close(); raise HTTPException(404,'Scholarship not found')
    con.execute('INSERT INTO applications(student_id,scholarship_id,status,applied_date,notes) VALUES(?,?,?,?,?) ON CONFLICT(student_id,scholarship_id) DO UPDATE SET status=excluded.status,notes=excluded.notes',(data.student_id,data.scholarship_id,data.status,data.applied_date,data.notes)); con.commit(); con.close(); return {'success':True}
@app.get('/api/applications')
def get_applications(student_id:str='demo-student'):
    con=db(); rows=con.execute('SELECT a.*,s.name,s.provider,s.amount,s.deadline,s.official_url FROM applications a JOIN scholarships s ON s.id=a.scholarship_id WHERE a.student_id=? ORDER BY a.id DESC',(student_id,)).fetchall(); con.close(); return [dict(r) for r in rows]
@app.patch('/api/applications/{scholarship_id}')
def update_application(scholarship_id:int,data:StatusIn,student_id:str='demo-student'):
    con=db(); cur=con.execute('UPDATE applications SET status=?, notes=COALESCE(?,notes) WHERE student_id=? AND scholarship_id=?',(data.status,data.notes,student_id,scholarship_id)); con.commit(); con.close()
    if cur.rowcount==0: raise HTTPException(404,'Application not found')
    return {'success':True}
@app.post('/api/eligibility/check')
def eligibility(payload:dict):
    sid=payload.get('scholarship_id'); level=(payload.get('education_level') or '').lower()
    con=db(); row=con.execute('SELECT * FROM scholarships WHERE id=?',(sid,)).fetchone(); con.close()
    if not row: raise HTTPException(404,'Scholarship not found')
    target=row['level'].lower(); matches=level in target or target in level
    return {'result':'Possibly Eligible' if matches else 'Needs profile review','reason':'Education level appears to match the listed level.' if matches else 'Your education level does not clearly match the listed level. Review the full criteria.','disclaimer':'This is preliminary guidance only, not an official eligibility decision.'}
@app.post('/api/chat')
def chat(data:ChatIn):
    q=data.question.lower()
    if any(x in q for x in ['document','certificate','paper','upload']): answer='Required documents depend on the scholarship. Common examples include previous-year marksheets, income certificate, identity proof, bank passbook/details, photograph, admission or fee receipt, and category certificate if applicable. Check the selected scholarship checklist and verify the final list on the official provider website.'
    elif any(x in q for x in ['eligib','qualif','criteria']): answer='Complete your student profile, open a scholarship and use the eligibility checker. GRANTLY compares profile details with listed criteria and gives preliminary guidance only. It is not an official decision.'
    elif any(x in q for x in ['deadline','last date']): answer='Check the deadline shown on the scholarship details page and confirm it on the official provider website because dates can change.'
    elif any(x in q for x in ['apply','application','track','status']): answer='Add a scholarship to your application tracker and update its status: Interested, Preparing, Applied, Under Review, Approved or Rejected. The actual application is submitted on the official provider website.'
    elif any(x in q for x in ['save','bookmark']): answer='Use the bookmark action on a scholarship card. Saved opportunities appear in Saved scholarships.'
    elif any(x in q for x in ['grantly','about','help','what is']): answer='GRANTLY helps students discover scholarships, understand listed eligibility criteria, save opportunities, prepare document checklists and track application progress. It does not award scholarships or guarantee selection.'
    elif any(x in q for x in ['source','official','verify']): answer='Each listing identifies its source and official link where available. Verify eligibility, documents, award amount and deadlines with the scholarship provider before applying.'
    else: answer='I can help only with GRANTLY and scholarship-related topics, such as eligibility, required documents, deadlines, application tracking and platform features.'
    return {'answer':answer,'scope':'scholarship-only'}
