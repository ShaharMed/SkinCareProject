# קובץ: app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    skin_type = data.get('skinType')
    conditions = data.get('conditions', [])

    # דוגמה ללוגיקת התאמה פשוטה
    recommendations = []
    if skin_type == "יבש":
        recommendations.append("קרם לחות עשיר")
    if skin_type == "שומני":
        recommendations.append("ג'ל ניקוי עדין לעור שמן")
    if "אקנה" in conditions:
        recommendations.append("סרום לטיפול בפצעונים")
    if "פיגמנטציה" in conditions:
        recommendations.append("קרם הבהרה עם ויטמין C")

    return jsonify({
        "recommendations": recommendations
    })

if __name__ == '__main__':
    app.run(debug=True)
