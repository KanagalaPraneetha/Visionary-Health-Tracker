from flask import Blueprint, request, jsonify, session
from .models import db, HealthMetric
from functools import wraps
from openai import OpenAI
import os

health_metric = Blueprint('health_metric', __name__)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=os.getenv("NEBIUS_API_KEY"),
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@health_metric.route('/api/health-metrics', methods=['POST'])
@login_required
def add_health_metric():
    try:
        data = request.json
        user_id = session['user_id']
        
        new_metric = HealthMetric(
            user_id=user_id,
            heart_rate=data.get('heart_rate'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            calorie_count=data.get('calorie_count')
        )
        
        db.session.add(new_metric)
        db.session.commit()
        
        return jsonify({
            "message": "Health metric added successfully",
            "metric_id": new_metric.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics', methods=['GET'])
@login_required
def get_health_metrics():
    try:
        user_id = session['user_id']
        metrics = HealthMetric.query.filter_by(user_id=user_id).order_by(HealthMetric.timestamp.desc()).all()
        
        return jsonify({
            "metrics": [{
                "id": metric.id,
                "heart_rate": metric.heart_rate,
                "blood_pressure_systolic": metric.blood_pressure_systolic,
                "blood_pressure_diastolic": metric.blood_pressure_diastolic,
                "calorie_count": metric.calorie_count,
                "timestamp": metric.timestamp.isoformat()
            } for metric in metrics]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-tips', methods=['GET'])
@login_required
def get_health_tips():
    try:
        user_id = session['user_id']
        latest_metric = HealthMetric.query.filter_by(user_id=user_id).order_by(HealthMetric.timestamp.desc()).first()
        
        if not latest_metric:
            return jsonify({"message": "No health metrics found"}), 404
            
        prompt = f"""
        Based on the following health metrics:
        Heart Rate: {latest_metric.heart_rate}
        Blood Pressure: {latest_metric.blood_pressure_systolic}/{latest_metric.blood_pressure_diastolic}
        Calorie Count: {latest_metric.calorie_count}

        Provide personalized health tips and recommendations for improving wellness.
        """

        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        health_tips = completion.choices[0].message.content
        
        return jsonify({
            "health_tips": health_tips,
            "metrics": {
                "heart_rate": latest_metric.heart_rate,
                "blood_pressure": f"{latest_metric.blood_pressure_systolic}/{latest_metric.blood_pressure_diastolic}",
                "calorie_count": latest_metric.calorie_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/<int:metric_id>', methods=['DELETE'])
@login_required
def delete_health_metric(metric_id):
    try:
        user_id = session['user_id']
        metric = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first()
        
        if not metric:
            return jsonify({"error": "Health metric not found"}), 404
        
        db.session.delete(metric)
        db.session.commit()
        
        return jsonify({"message": "Health metric deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/<int:metric_id>', methods=['PUT'])
@login_required
def update_health_metric(metric_id):
    try:
        user_id = session['user_id']
        metric = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first()
        
        if not metric:
            return jsonify({"error": "Health metric not found"}), 404
        
        data = request.json
        metric.heart_rate = data.get('heart_rate', metric.heart_rate)
        metric.blood_pressure_systolic = data.get('blood_pressure_systolic', metric.blood_pressure_systolic)
        metric.blood_pressure_diastolic = data.get('blood_pressure_diastolic', metric.blood_pressure_diastolic)
        metric.calorie_count = data.get('calorie_count', metric.calorie_count)
        
        db.session.commit()
        
        return jsonify({"message": "Health metric updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/<int:metric_id>', methods=['GET'])
@login_required
def get_health_metric(metric_id):
    try:
        user_id = session['user_id']
        metric = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first()
        
        if not metric:
            return jsonify({"error": "Health metric not found"}), 404
        
        return jsonify({
            "id": metric.id,
            "heart_rate": metric.heart_rate,
            "blood_pressure_systolic": metric.blood_pressure_systolic,
            "blood_pressure_diastolic": metric.blood_pressure_diastolic,
            "calorie_count": metric.calorie_count,
            "timestamp": metric.timestamp.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/summary', methods=['GET'])
@login_required
def get_health_metrics_summary():
    try:
        user_id = session['user_id']
        metrics = HealthMetric.query.filter_by(user_id=user_id).all()
        
        if not metrics:
            return jsonify({"message": "No health metrics found"}), 404
        
        heart_rate_avg = sum([metric.heart_rate for metric in metrics]) / len(metrics)
        bp_systolic_avg = sum([metric.blood_pressure_systolic for metric in metrics]) / len(metrics)
        bp_diastolic_avg = sum([metric.blood_pressure_diastolic for metric in metrics]) / len(metrics)
        calorie_count_avg = sum([metric.calorie_count for metric in metrics]) / len(metrics)
        
        return jsonify({
            "heart_rate_avg": heart_rate_avg,
            "blood_pressure_systolic_avg": bp_systolic_avg,
            "blood_pressure_diastolic_avg": bp_diastolic_avg,
            "calorie_count_avg": calorie_count_avg
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/summary', methods=['DELETE'])
@login_required
def delete_health_metrics():
    try:
        user_id = session['user_id']
        metrics = HealthMetric.query.filter_by(user_id=user_id).all()
        
        if not metrics:
            return jsonify({"message": "No health metrics found"}), 404
        
        for metric in metrics:
            db.session.delete(metric)
        
        db.session.commit()
        
        return jsonify({"message": "All health metrics deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500