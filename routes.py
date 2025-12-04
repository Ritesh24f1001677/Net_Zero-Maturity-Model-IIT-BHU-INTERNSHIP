# routes.py
from flask import (
    render_template, request, redirect, url_for,
    flash, session
)
from flask_login import (
    login_user, logout_user, login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
from functools import wraps

from models import db, User, Response
from suggestion_engine import generate_dynamic_suggestion


def register_routes(app):
    # ----------------------------------------------------------------------
    # ADMIN CREDENTIALS (default if not using Admin table)
    # ----------------------------------------------------------------------
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "bhu123"

    # ----------------------------------------------------------------------
    # ADMIN CHECK DECORATOR
    # ----------------------------------------------------------------------
    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("is_admin"):
                flash("Admin access required!", "danger")
                return redirect(url_for("admin_login"))
            return f(*args, **kwargs)
        return decorated

    # ----------------------------------------------------------------------
    # LANDING PAGE
    # ----------------------------------------------------------------------
    @app.route("/")
    def landing_page():
        if session.get("is_admin"):
            return redirect(url_for("admin_dashboard"))

        if current_user.is_authenticated:
            if not current_user.onboard_complete:
                return redirect(url_for("onboarding"))
            return redirect(url_for("home"))

        return render_template("home_landing.html")

    # ----------------------------------------------------------------------
    # ADMIN LOGIN
    # ----------------------------------------------------------------------
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session["is_admin"] = True
                flash("Admin login successful!", "success")
                return redirect(url_for("admin_dashboard"))

            flash("Invalid admin credentials!", "danger")

        return render_template("admin_login.html")

    # ----------------------------------------------------------------------
    # ADMIN LOGOUT
    # ----------------------------------------------------------------------
    @app.route("/admin/logout")
    def admin_logout():
        session.pop("is_admin", None)
        flash("Admin logged out.", "info")
        return redirect(url_for("landing_page"))

    @app.route("/admin/dashboard")
    @admin_required
    def admin_dashboard():
        # Total counts
        total_users = User.query.count()
        total_responses = Response.query.count()

        # Latest 10 users
        recent_users = User.query.order_by(User.id.desc()).limit(10).all()

        # Prepare responses grouped by user
        users_with_responses = []
        for u in recent_users:
            responses = Response.query.filter_by(user_id=u.id).order_by(Response.level).all()
            if responses:
                u.responses = responses  # Attach responses to user
                users_with_responses.append(u)

        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_responses=total_responses,
            recent_users=recent_users,
            users_with_responses=users_with_responses  # Pass this to template
        )


    # ======================================================================
    # USER TRANSLATIONS & QUESTION BANK
    # ======================================================================
    TRANSLATIONS = {
        "en": {
            "welcome": "Welcome",
            "home_title": "Carbon Emission Analysis - Home",
            "questionnaire": "Questionnaire",
            "profile": "Profile",
            "performance": "Performance",
            "suggestions": "Suggestions",
            "documentaries": "Documentaries",
            "analysis": "Analysis",
            "start": "Start",
            "next_level_locked": "Complete previous level to unlock this level.",
            "onboard_title": "5 quick steps to get started"
        },
        "hi": {
            "welcome": "स्वागत है",
            "home_title": "कार्बन उत्सर्जन विश्लेषण - होम",
            "questionnaire": "प्रश्नावली",
            "profile": "प्रोफ़ाइल",
            "performance": "प्रदर्शन",
            "suggestions": "सुझाव",
            "documentaries": "डॉक्यूमेंटरी",
            "analysis": "विश्लेषण",
            "start": "शुरू करें",
            "next_level_locked": "इस स्तर को अनलॉक करने के लिए पिछले स्तर को पूरा करें।",
            "onboard_title": "शुरू करने के लिए 5 त्वरित कदम"
        }
    }

    # Load questions
    with open(os.path.join(os.path.dirname(__file__), "questionnaire.json"), "r", encoding="utf-8") as f:
        QUESTION_BANK = json.load(f)

    CATEGORIES_AS_LEVELS = {str(k): v for k, v in QUESTION_BANK.get("categories_as_levels", {}).items()}
    LEVELS = QUESTION_BANK.get("levels", {})

    # ----------------------------------------------------------------------
    # Helper Functions
    # ----------------------------------------------------------------------
    def current_language():
        if current_user.is_authenticated and getattr(current_user, "language", None):
            return current_user.language
        return session.get("lang", "en")

    def compute_level_maturity_from_percent(pct):
        if pct >= 75: return 4
        if pct >= 50: return 3
        if pct >= 25: return 2
        return 1

    def level_name(level_int):
        return LEVELS.get(str(level_int), f"Level {level_int}")

    def get_next_attempt_number(user_id):
        last_attempt = db.session.query(db.func.max(Response.attempt_number)).filter_by(user_id=user_id).scalar()
        if not last_attempt:
            return 1
        level_count = Response.query.filter_by(user_id=user_id, attempt_number=last_attempt).count()
        return last_attempt if level_count < 4 else last_attempt + 1

    # ======================================================================
    # USER REGISTRATION
    # ======================================================================
    @app.route("/register", methods=["GET", "POST"])
    def register():
        t = TRANSLATIONS[current_language()]
        if request.method == "POST":
            email = request.form.get("email").lower().strip()
            password = request.form.get("password")
            name = request.form.get("name")

            if User.query.filter_by(email=email).first():
                flash("Email already exists!", "warning")
                return redirect(url_for("login"))

            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                name=name
            )
            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for("login"))

        return render_template("register.html", translations=t)

    # ======================================================================
    # USER LOGIN
    # ======================================================================
    @app.route("/login", methods=["GET", "POST"])
    def login():
        t = TRANSLATIONS[current_language()]
        if request.method == "POST":
            login_id = request.form.get("login_id").strip().lower()
            password = request.form.get("password")

            # Admin login bypass
            if login_id == ADMIN_USERNAME.lower() and password == ADMIN_PASSWORD:
                session["is_admin"] = True
                flash("Admin login successful!", "success")
                return redirect(url_for("admin_dashboard"))

            user = User.query.filter_by(email=login_id).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for("onboarding") if not user.onboard_complete else url_for("home"))

            flash("Invalid credentials!", "danger")

        return render_template("login.html", translations=t)

    # ======================================================================
    # LOGOUT
    # ======================================================================
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out!", "info")
        return redirect(url_for("landing_page"))

    # ======================================================================
    # ONBOARDING
    # ======================================================================
    @app.route("/onboarding", methods=["GET", "POST"])
    @login_required
    def onboarding():
        t = TRANSLATIONS[current_language()]
        if request.method == "POST":
            current_user.language = request.form.get("language", "en")
            current_user.step1 = request.form.get("step1")
            current_user.step2 = request.form.get("step2")
            step3_val = request.form.get("step3")
            current_user.step3 = int(step3_val) if step3_val and step3_val.isdigit() else None
            current_user.step4 = request.form.get("step4")
            current_user.step5 = request.form.get("step5")
            current_user.onboard_complete = True
            db.session.commit()
            flash("Onboarding complete!", "success")
            return redirect(url_for("home"))

        return render_template("onboarding.html", translations=t)

    # ======================================================================
    # HOME PAGE
    # ======================================================================
    @app.route("/home")
    @login_required
    def home():
        t = TRANSLATIONS[current_language()]
        lang = current_language()

        responses = Response.query.filter_by(user_id=current_user.id).all()
        final_level = None

        if responses:
            best_scores = {}
            for r in responses:
                if r.level not in best_scores or r.score > best_scores[r.level]:
                    best_scores[r.level] = r.score
            total_best_score = sum(best_scores.values())
            final_level = (
                1 if total_best_score <= 9 else
                2 if total_best_score <= 18 else
                3 if total_best_score <= 27 else
                4
            )

        return render_template("home.html",
                               translations=t,
                               final_level=final_level,
                               lang=lang)

    # ======================================================================
    # SET LANGUAGE
    # ======================================================================
    @app.route("/set_language/<lang>")
    @login_required
    def set_language(lang):
        if lang in ["en", "hi"]:
            session['lang'] = lang
            if current_user.is_authenticated:
                current_user.language = lang
                db.session.commit()
        return redirect(request.referrer or url_for("home"))

    # ======================================================================
    # PROFILE PAGE
    # ======================================================================
    @app.route("/profile")
    @login_required
    def profile():
        t = TRANSLATIONS.get(current_language(), TRANSLATIONS['en'])
        return render_template("profile.html", translations=t)

    # ======================================================================
    # REMAINING QUESTIONNAIRE LOGIC (PERFORMANCE, SUGGESTIONS ETC.)
    # ======================================================================
    # All questionnaire, level, performance, insights, suggestions routes remain the same
    # as your previous implementation. PostgreSQL requires no code changes here except for db.session.commit().


    # --------------------------
    # Questionnaire Index
    # --------------------------
    @app.route("/questionnaire")
    @login_required
    def questionnaire_index():
        t = TRANSLATIONS.get(current_language(), TRANSLATIONS['en'])

        current_attempt = get_next_attempt_number(current_user.id)
        session['current_attempt'] = current_attempt

        completed_levels = {
            r.level for r in Response.query.filter_by(
                user_id=current_user.id,
                attempt_number=current_attempt
            ).all()
        }

        levels_unlocked = [1]
        for lvl in range(2, 5):
            if (lvl - 1) in completed_levels:
                levels_unlocked.append(lvl)
            else:
                break

        session['levels_unlocked'] = levels_unlocked

        last_attempt = current_attempt - 1
        if last_attempt >= 1:
            last_count = Response.query.filter_by(
                user_id=current_user.id,
                attempt_number=last_attempt
            ).count()
            if last_count == 4:
                flash(f"Starting new attempt #{current_attempt}", "info")

        return render_template("questionnaire_index.html",
                               translations=t,
                               completed_levels=completed_levels,
                               levels_unlocked=levels_unlocked,
                               categories_as_levels=CATEGORIES_AS_LEVELS,
                               levels=LEVELS,
                               current_lang=current_language())

    # --------------------------
    # Questionnaire Level
    # --------------------------
    @app.route("/questionnaire/level/<int:level>", methods=["GET", "POST"])
    @login_required
    def questionnaire_level(level):
        level_str = str(level)
        if level_str not in CATEGORIES_AS_LEVELS:
            flash("Invalid level.", "danger")
            return redirect(url_for("questionnaire_index"))

        current_attempt = session.get('current_attempt') or get_next_attempt_number(current_user.id)
        levels_unlocked = session.get('levels_unlocked', [1])

        if level not in levels_unlocked:
            flash(TRANSLATIONS[current_language()]['next_level_locked'], "warning")
            return redirect(url_for("questionnaire_index"))

        questions = CATEGORIES_AS_LEVELS[level_str]["questions"]

        if request.method == "POST":
            total_score = 0.0
            total_min_score = 0.0
            total_max_score = 0.0
            fulfilled_attributes = 0
            total_attributes_in_level = 0

            details_dict = {}
            parameter_map = {}

            for q in questions:
                qid = q.get("id")
                ans_key = request.form.get(f"q_{qid}", "").strip()

                question_parameter = q.get("parameter", q.get("category", "General"))
                parameter_map.setdefault(question_parameter, {
                    "total": 0, "score": 0.0, "min": 0.0, "max": 0.0, "questions": []
                })

                parameter_map[question_parameter]["total"] += 1
                total_attributes_in_level += 1

                options = q.get("options", {})
                option_scores = [
                    float(opt.get("score", 0.0)) if isinstance(opt, dict) else float(opt)
                    for opt in options.values()
                ] if options else [0.0]

                q_min = min(option_scores)
                q_max = max(option_scores)
                total_min_score += q_min
                total_max_score += q_max

                selected_score = 0.0
                if ans_key in options:
                    opt_val = options[ans_key]
                    selected_score = float(opt_val.get("score", 0.0)) if isinstance(opt_val, dict) else float(opt_val)

                total_score += selected_score
                parameter_map[question_parameter]["score"] += selected_score
                parameter_map[question_parameter]["min"] += q_min
                parameter_map[question_parameter]["max"] += q_max

                if selected_score > 0:
                    fulfilled_attributes += 1

                parameter_map[question_parameter]["questions"].append({
                    "id": qid,
                    "text": q.get("text"),
                    "selected": ans_key,
                    "selected_score": selected_score,
                    "options": options
                })

            percent_of_level = (total_score / total_max_score * 100) if total_max_score > 0 else 0.0
            level_maturity = compute_level_maturity_from_percent(percent_of_level)

            details_dict["_summary"] = {
                "level": level,
                "score_total": total_score,
                "score_min": total_min_score,
                "score_max": total_max_score,
                "percent_of_level": percent_of_level,
                "fulfilled_attributes": fulfilled_attributes,
                "total_attributes": total_attributes_in_level,
                "parameter_summary": parameter_map,
                "submitted_at": datetime.utcnow().isoformat() + "Z"
            }

            response = Response(
                user_id=current_user.id,
                level=level,
                score=total_score,
                maturity_level=level_maturity,
                details=json.dumps(details_dict),
                attempt_number=current_attempt
            )

            db.session.add(response)
            db.session.commit()

            if level < 4:
                unlocked = session.get('levels_unlocked', [1])
                if level + 1 not in unlocked:
                    unlocked.append(level + 1)
                session['levels_unlocked'] = unlocked

            flash(f"Level {level} completed. Score: {total_score})",
                  "success")
            return redirect(url_for("questionnaire_index"))

        t = TRANSLATIONS.get(current_language(), TRANSLATIONS['en'])
        return render_template("questionnaire_level.html",
                               categories_as_levels=CATEGORIES_AS_LEVELS,
                               level=level,
                               translations=t,
                               current_lang=current_language())

    # --------------------------
    # Start New Attempt
    # --------------------------
    @app.route("/start_new_attempt")
    @login_required
    def start_new_attempt():
        next_attempt = get_next_attempt_number(current_user.id)
        last_count = Response.query.filter_by(
            user_id=current_user.id,
            attempt_number=next_attempt - 1
        ).count()

        if next_attempt > 1 and last_count < 4:
            flash("Finish all levels before starting a new attempt.", "warning")
            return redirect(url_for("performance"))

        flash(f"Starting new attempt #{next_attempt}", "info")
        session['current_attempt'] = next_attempt
        session['levels_unlocked'] = [1]
        return redirect(url_for("questionnaire_index"))

    # --------------------------
    # Performance
    # --------------------------
    @app.route("/performance")
    @login_required
    def performance():
        t = TRANSLATIONS.get(current_language(), TRANSLATIONS['en'])

        responses = Response.query.filter_by(
            user_id=current_user.id
        ).order_by(Response.attempt_number, Response.level).all()

        LEVEL_GROUP_NAMES = {
            1: "Awareness",
            2: "Engagement",
            3: "Action",
            4: "Impact"
        }

        grouped_by_attempt = {}
        for r in responses:
            att = r.attempt_number or 1
            grouped_by_attempt.setdefault(att, [])

            details = json.loads(r.details) if r.details else {}
            score_max = details.get("_summary", {}).get("score_max", r.score)

            grouped_by_attempt[att].append({
                "id": r.id,
                "level": r.level,
                "group_name": LEVEL_GROUP_NAMES.get(r.level, f"Level {r.level}"),
                "score": r.score,
                "score_max": score_max,
                "level_label": level_name(r.level)
            })

        last_attempt = max(grouped_by_attempt.keys()) if grouped_by_attempt else 0
        start_new_enabled = (len(grouped_by_attempt.get(last_attempt, [])) == 4) if last_attempt else True

        return render_template("performance.html",
                               translations=t,
                               grouped_by_attempt=grouped_by_attempt,
                               start_new_enabled=start_new_enabled,
                               lang=current_language())

    # --------------------------
    # Performance Insights
    # --------------------------
    @app.route("/performance_insights")
    @login_required
    def performance_insights():

        responses = Response.query.filter_by(
            user_id=current_user.id
        ).order_by(Response.attempt_number).all()

        attempts = [r.attempt_number for r in responses]
        unique_attempts = sorted(list(set(attempts)))
        scores = [r.score for r in responses]
        levels = [r.level for r in responses]
        maturity = [r.maturity_level for r in responses]
        dates = [r.created_at.strftime("%d %b %Y") for r in responses]

        group_names = []
        for lvl in levels:
            if lvl == 1:
                group_names.append("Awareness and Engagement")
            elif lvl == 2:
                group_names.append("Knowledge & Capabilities")
            elif lvl == 3:
                group_names.append("Planning & Strategies")
            elif lvl == 4:
                group_names.append("Physical Actions")
            else:
                group_names.append("Unknown")

        return render_template("performance_insights.html",
                               attempts=unique_attempts,
                               scores=scores,
                               levels=levels,
                               group_names=group_names,
                               maturity=maturity,
                               dates=dates,
                               translations=TRANSLATIONS.get(
                                   current_language(),
                                   TRANSLATIONS['en']
                               ))

    # --------------------------
    # Suggestions Page
    # --------------------------
    @app.route("/suggestions")
    @login_required
    def suggestions():
        t = TRANSLATIONS.get(current_language(), TRANSLATIONS['en'])
        responses = Response.query.filter_by(
            user_id=current_user.id
        ).order_by(Response.level).all()

        ai_suggestion = generate_dynamic_suggestion(current_user, responses)
        return render_template("suggestions.html",
                               translations=t,
                               suggestion=ai_suggestion)
