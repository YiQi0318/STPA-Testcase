import openai
import os
from openai import OpenAI
import re
from sentence_transformers import SentenceTransformer, util


api_key = os.getenv('OPENAI_API_KEY', '[Your Key]')
client = OpenAI(api_key=api_key)

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def update_context(text, prompt_template, threshold=0.8, stop_threshold=3):
    uca_sections = text.split('UCA')
    updated_text = uca_sections[0]
    for section in uca_sections[1:]:
        uca_id = section.split(':')[0].strip()
        context_match = re.search(r'Context:\s*(.*)', section, re.DOTALL)
        
        if context_match:
            context = context_match.group(1).strip()
            context_sentences = [sentence.strip() for sentence in context.split('\n') if sentence.strip()]
            prompt = prompt_template.format(context=context)
            consecutive_similar_count = 0  # Counter for consecutive similar sentences
            
            while consecutive_similar_count < stop_threshold:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    # prompt=prompt,
                    max_tokens=200,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                new_context = response.choices[0].message.content.strip()
                new_sentences = [sentence.strip() for sentence in new_context.split('\n') if sentence.strip()]
                
                # Debug output
                print(f"Generated sentences: {new_sentences}")
                
                # Check similarity for each new sentence
                is_similar = False
                for new_sentence in new_sentences:
                    for existing_sentence in context_sentences:
                        similarity = compare_similarity(existing_sentence, new_sentence)
                        print(f"Comparing: '{existing_sentence}' with '{new_sentence}' -> Similarity: {similarity}")
                        if similarity >= threshold:
                            is_similar = True
                            break
                    if is_similar:
                        break
                
                if not is_similar:
                    print(f"Adding new sentences: {new_sentences}")
                    context_sentences.extend(new_sentences)
                    section = section.replace(context, '\n'.join(context_sentences))
                    context = '\n'.join(context_sentences)  # Update context for the next iteration
                    consecutive_similar_count = 0  # Reset counter
                else:
                    consecutive_similar_count += 1  # Increment counter
                
                # Debug output
                print(f"Consecutive similar count: {consecutive_similar_count}")
            
        updated_text += f'UCA{section}'
    
    return updated_text

def compare_similarity(sentence1, sentence2):
    sentence1_embedding = model.encode(sentence1, convert_to_tensor=True)
    sentence2_embedding = model.encode(sentence2, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(sentence1_embedding, sentence2_embedding).item()
    return similarity

def main():
    uca_path = "[bbw_uca.txt]"
    update_uca_path = "[bbw_update_uca.txt]"
    
    prompt_template = "Here is the context:\n\n{context}\n\nIs there any new context to add for each UCA? If yes, directly add the new context to the 'context' part. If no, it should have a threshold to stop asking."

    input_text = read_file(uca_path)
    updated_text = update_context(input_text, prompt_template, threshold=0.8, stop_threshold=3)
    write_file(update_uca_path, updated_text)

if __name__ == "__main__":
    main()