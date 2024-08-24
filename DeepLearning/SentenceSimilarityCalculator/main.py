from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

class SentenceSimilarityChecker:
    """
    Tokenization:
        Purpose: Converts raw text (sentences) into token IDs for model processing.
        Effect: Prepares sentences for embedding by transforming text into a format the model can process.
    
    Embedding Generation:
        Purpose: Creates vector representations of the sentences.
        Effect: Encodes each token into a dense vector space, capturing semantic information about the sentences.

    Pooling:
        Purpose: Combines token embeddings into a single vector per sentence.
        Effect: Applies mean pooling to aggregate embeddings based on attention masks, summarizing the entire sentence.

    Normalization:
        Purpose: Scales embeddings to unit length.
        Effect: Ensures embeddings are normalized, enabling consistent and reliable similarity comparisons.

    Cosine Similarity:
        Purpose: Measures similarity between sentence embeddings.
        Effect: Calculates how closely the embeddings of the new sentence match those of existing sentences, identifying potential similarity based on the scores.
    """

    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def compute_embeddings(self, sentences):
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt', max_length=512)
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings

    def check_similarity(self, existing_sentences, new_sentence, threshold=0.8):
        existing_embeddings = self.compute_embeddings(existing_sentences)
        new_sentence_embedding = self.compute_embeddings([new_sentence])
        cosine_similarities = F.cosine_similarity(new_sentence_embedding, existing_embeddings)
        print("Cosine similarities between new sentence and existing sentences:")
        similarity_detected = False
        for i, sim in enumerate(cosine_similarities):
            print(f"Sentence {i + 1}: {sim.item()}")
            if sim.item() > threshold:
                print("Potential similarity detected!")
                similarity_detected = True
                break
        if not similarity_detected:
            print("No significant similarity detected.")

checker = SentenceSimilarityChecker()

existing_sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "A fast, dark fox leaps across a lazy hound.",
    "A swift fox hops over a sleepy dog.",
    "Subtracting two numbers is simple.",
    "The rapid fox bounds over the inert dog."
]

new_sentence = "The rapid fox bounds over the inert dog."

checker.check_similarity(existing_sentences, new_sentence)
