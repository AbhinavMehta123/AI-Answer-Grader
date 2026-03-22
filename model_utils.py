from sentence_transformers import SentenceTransformer, util
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

def grade_answer(question, model_answer, student_answer, keywords_input):

    emb_model = model.encode(model_answer, convert_to_tensor=True)
    emb_student = model.encode(student_answer, convert_to_tensor=True)
    emb_question = model.encode(question, convert_to_tensor=True)

    bert_score = util.pytorch_cos_sim(emb_model, emb_student).item() * 10
    relevance = util.pytorch_cos_sim(emb_question, emb_student).item()
    relevance_score = relevance * 10

    word_count = len(re.findall(r'\w+', student_answer))

    length_penalty = 0
    if word_count < 8:
        length_penalty = 2
    elif word_count < 15:
        length_penalty = 1

    keyword_score = 0
    if keywords_input:
        keywords = [k.strip().lower() for k in keywords_input.split(",")]
        matched = 0

        for k in keywords:
            combined_text = model_answer + " " + k
            emb_kw = model.encode(combined_text, convert_to_tensor=True)

            sim = util.pytorch_cos_sim(emb_kw, emb_student).item()

            if sim > 0.55:
                matched += 1

        keyword_score = (matched / len(keywords)) * 10

    final_score = (bert_score * 0.75) + (keyword_score * 0.25)
    final_score = max(0, min(10, final_score - length_penalty))

    return round(final_score, 2), round(bert_score, 2), round(relevance_score, 2), round(keyword_score, 2), word_count, relevance