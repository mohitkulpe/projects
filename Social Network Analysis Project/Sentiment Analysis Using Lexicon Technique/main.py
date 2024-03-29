# coding: utf-8


from collections import Counter, defaultdict
from itertools import chain, combinations
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from scipy.sparse import csr_matrix
from sklearn.cross_validation import KFold
from sklearn.linear_model import LogisticRegression
import string
import tarfile
import urllib.request


def download_data():
    """ Download and unzip data.
    """
    # URL of database
    url = 'https://www.xyz.com/.../imdb.tgz'
    urllib.request.urlretrieve(url, 'imdb.tgz')
    tar = tarfile.open("imdb.tgz")
    tar.extractall()
    tar.close()


def read_data(path):
    """
    Walks all subdirectories of this path and reads all
    the text files and labels.
   
    Params:
      path....path to files
    Returns:
      docs.....list of strings, one per document
      labels...list of ints, 1=positive, 0=negative label.
               Inferred from file path (i.e., if it contains
               'pos', it is 1, else 0)
    """
    


def tokenize(doc, keep_internal_punct=False):
    """
    Tokenize a string.
    The string should be converted to lowercase.
    If keep_internal_punct is False, then return only the alphanumerics (letters, numbers and underscore).
    If keep_internal_punct is True, then also retain punctuation that
    is inside of a word. E.g., in the example below, the token "isn't"
    is maintained when keep_internal_punct=True; otherwise, it is
    split into "isn" and "t" tokens.

    Params:
      doc....a string.
      keep_internal_punct...see above
    Returns:
      a numpy array containing the resulting tokens.

    
    """
   
    doc = doc.lower()
    
    if keep_internal_punct == False:
        
        doc_f = re.sub('[\W_]+',' ',doc).split()
        
        #print(doc_f)
        
        return (np.array(doc_f))
        

    if keep_internal_punct == True:
        
        doc = doc.split()
        doc_t = []
        
        rm_punct = str(string.punctuation.replace("_", ""))
        
        for i in doc:
            doc_t.append(i.strip(rm_punct))
            
        #print(doc_t)
        
        return (np.array(doc_t))
        
       
    pass



def token_features(tokens, feats):
    """
    Add features for each token. The feature name
    is pre-pended with the string "token=".
    Note that the feats dict is modified in place,
    so there is no return value.

    Params:
      tokens...array of token strings from a document.
      feats....dict from feature name to frequency
    Returns:
      nothing; feats is modified in place.

    
    """
    
    
    for t in tokens:
        s = 'token='+t
        if (s in feats):
            feats[s] +=1
        else:
            feats[s] =1
    
    feats = (sorted(feats.items()))     

    #print (feats)
    
    pass


def token_pair_features(tokens, feats, k=3):
    """
    Compute features indicating that two words occur near
    each other within a window of size k.

    For example [a, b, c, d] with k=3 will consider the
    windows: [a,b,c], [b,c,d]. In the first window,
    a_b, a_c, and b_c appear; in the second window,
    b_c, c_d, and b_d appear. This example is in the
    doctest below.
    Note that the order of the tokens in the feature name
    matches the order in which they appear in the document.
    (e.g., a__b, not b__a)

    Params:
      tokens....array of token strings from a document.
      feats.....a dict from feature to value
      k.........the window size (3 by default)
    Returns:
      nothing; feats is modified in place.

   
    """
    
    
    win_num = len(tokens)-k+1
    c = Counter()
    win = []

    for i in range(0,win_num):
        win.append(tokens[i:i+k])

    for j in win:
        comb = combinations(j,2)
        for c1 in comb:
            c['token_pair='+c1[0]+'__'+c1[1]]+=1

    for key,value in c.items():
        feats[key] = value

    feats = sorted(feats.items())
    
    #print (feats)
    
    pass


neg_words = set(['bad', 'hate', 'horrible', 'worst', 'boring'])
pos_words = set(['awesome', 'amazing', 'best', 'good', 'great', 'love', 'wonderful'])


def lexicon_features(tokens, feats):
    """
    Add features indicating how many time a token appears that matches either
    the neg_words or pos_words (defined above). The matching should ignore
    case.

    Params:
      tokens...array of token strings from a document.
      feats....dict from feature name to frequency
    Returns:
      nothing; feats is modified in place.

    
    """
   
    
    lower_tokens = [t.lower() for t in tokens]

    feats['neg_words'] = 0
    feats['pos_words'] = 0
    

    for lt in lower_tokens:
        
        if lt in neg_words:
            feats['neg_words'] += 1
            
        elif lt in pos_words:
            feats['pos_words'] += 1 

    feats = sorted(feats.items())
    
    #print (feats)

    pass


def featurize(tokens, feature_fns):
    """
    Compute all features for a list of tokens from
    a single document.

    Params:
      tokens........array of token strings from a document.
      feature_fns...a list of functions, one per feature
    Returns:
      list of (feature, value) tuples, SORTED alphabetically
      by the feature name.

    
    """
    
    feats = defaultdict(lambda: 0)
    
    for f in feature_fns:
        f(tokens, feats)

    return sorted(feats.items())
    
    # print (feats)
    
    pass


def vectorize(tokens_list, feature_fns, min_freq, vocab=None):
    """
    Given the tokens for a set of documents, create a sparse
    feature matrix, where each row represents a document, and
    each column represents a feature.

    Params:
      tokens_list...a list of lists; each sublist is an
                    array of token strings from a document.
      feature_fns...a list of functions, one per feature
      min_freq......Remove features that do not appear in
                    at least min_freq different documents.
    Returns:
      - a csr_matrix: See https://goo.gl/f5TiF1 for documentation.
      This is a sparse matrix (zero values are not stored).
      - vocab: a dict from feature name to column index. NOTE
      that the columns are sorted alphabetically (so, the feature
      "token=great" is column 0 and "token=horrible" is column 1
      because "great" < "horrible" alphabetically),

    
    """
    
    
    if vocab == None:
        
        feature_count = Counter()
        feature_list = []
                        

        i = 0
        for j in tokens_list:
            feature_dict = defaultdict(list)
            
            feature = featurize(j, feature_fns)
            for k in feature:
                if k[1] > 0:
                    feature_dict[k[0]]=k[1]
                    feature_count[k[0]] += 1

            feature_list.append(feature_dict)
            i += 1

        
        vocab = defaultdict()
        
        l = 0
        
        for key,value in sorted(feature_count.items()):
            if feature_count[key] >= min_freq:
                vocab[key] = l
                l += 1
        
        
        
        document = []
        column = []
        row = []
        
        
        m = 0
        
        for f in feature_list:
            for e in f:
                if e in vocab:
                    document.append(f[e])
                    column.append(vocab[e])
                    row.append(m)
            m += 1

        X = csr_matrix((document,(row,column)))
        
        #print (X.dtype)
        X = X.astype(np.int64)
        #print (X.dtype)

        return X,vocab
    

    else:
        
        feature_count = Counter()
               
        feature_list = []


        i = 0
        
        for j in tokens_list:
            feature_dict = defaultdict(list)
            feature = featurize(j, feature_fns)
            for k in feature:
                if k[1] > 0:
                    feature_dict[k[0]] = k[1]
                    feature_count[k[0]] += 1

            feature_list.append(feature_dict)
            
            i += 1
        
        
        
        document = []
        column = []
        row = []
                
        l = 0
        
        for f in feature_list:
            for e in f:
                if e in vocab:
                    document.append(f[e])
                    column.append(vocab[e])
                    row.append(l)
                    
            l += 1

        X = csr_matrix((document, (row, column)))
        
        X = X.astype(np.int64)
        
        #print (X.dtype)
        
        return X,vocab
    
    
    pass


def accuracy_score(truth, predicted):
    """ Compute accuracy of predictions.
    
    Params:
      truth.......array of true labels (0 or 1)
      predicted...array of predicted labels (0 or 1)
    """
    return len(np.where(truth==predicted)[0]) / len(truth)


def cross_validation_accuracy(clf, X, labels, k):
    """
    Compute the average testing accuracy over k folds of cross-validation. You
    can use sklearn's KFold class here (no random seed, and no shuffling
    needed).

    Params:
      clf......A LogisticRegression classifier.
      X........A csr_matrix of features.
      labels...The true labels for each instance in X
      k........The number of cross-validation folds.

    Returns:
      The average testing accuracy of the classifier
      over each fold of cross-validation.
    """
    
    
    kf = KFold(len(labels),k)
    accuracy_list = []

    for train, test in kf:
        clf.fit(X[train], labels[train])
        pred = clf.predict(X[test])
        accuracy_list.append(accuracy_score(labels[test], pred))
    
    acc = np.mean(accuracy_list)
    
    #print (acc)
    
    return acc

    pass


def eval_all_combinations(docs, labels, punct_vals,
                          feature_fns, min_freqs):
    """
    Enumerate all possible classifier settings and compute the
    cross validation accuracy for each setting. We will use this
    to determine which setting has the best accuracy.

    For each setting, construct a LogisticRegression classifier
    and compute its cross-validation accuracy for that setting.

    In addition to looping over possible assignments to
    keep_internal_punct and min_freqs, we will enumerate all
    possible combinations of feature functions. So, if
    feature_fns = [token_features, token_pair_features, lexicon_features],
    then we will consider all 7 combinations of features (see Log.txt
    for more examples).

    Params:
      docs..........The list of original training documents.
      labels........The true labels for each training document (0 or 1)
      punct_vals....List of possible assignments to
                    keep_internal_punct (e.g., [True, False])
      feature_fns...List of possible feature functions to use
      min_freqs.....List of possible min_freq values to use
                    (e.g., [2,5,10])

    Returns:
      A list of dicts, one per combination. Each dict has
      four keys:
      'punct': True or False, the setting of keep_internal_punct
      'features': The list of functions used to compute features.
      'min_freq': The setting of the min_freq parameter.
      'accuracy': The average cross_validation accuracy for this setting, using 5 folds.

      This list should be SORTED in descending order of accuracy.

      
    """
    
    
    combination_list = []
    
    for i in range(1,len(feature_fns)+1):
        for c in combinations(feature_fns,i):
            combination_list.append(list(c))

    ptrue_token = [tokenize(d,keep_internal_punct=True) for d in docs]
    pfalse_token = [tokenize(d,keep_internal_punct=False) for d in docs]
    
    
    cv_result = []
    
    for cl in combination_list:
        for pv in punct_vals:
            for mf in min_freqs:
                if pv == True:
                    X,vocab= vectorize(ptrue_token, cl,mf)
                    cv = cross_validation_accuracy(LogisticRegression(),X,labels,5)
                    cv_result.append({'features':cl ,'punct':pv, 'accuracy':cv,'min_freq':mf})

                else:
                    X,vocab = vectorize(pfalse_token, cl,mf)
                    cv = cross_validation_accuracy(LogisticRegression(), X, labels, 5)
                    cv_result.append({'features': cl, 'punct': pv, 'accuracy': cv, 'min_freq': mf})

    sorted_acc = sorted(cv_result, key=lambda d: -d['accuracy'])
    
    # print (sorted_result)
    
    return (sorted_acc)


    pass


def plot_sorted_accuracies(results):
    """
    Plot all accuracies from the result of eval_all_combinations
    in ascending order of accuracy.
    Save to "accuracies.png".
    """
    
    
    sorted_accs = sorted(results,key = lambda d:d['accuracy'])
    point_list = []
    
    for r in sorted_accs:
        point_list.append(r['accuracy'])

    plt.plot(point_list)
    plt.xlabel("setting")
    plt.ylabel("accuracy")
    plt.savefig("accuracies.png")
    
    
    pass


def mean_accuracy_per_setting(results):
    """
    To determine how important each model setting is to overall accuracy,
    we'll compute the mean accuracy of all combinations with a particular
    setting. For example, compute the mean accuracy of all runs with
    min_freq=2.

    Params:
      results...The output of eval_all_combinations
    Returns:
      A list of (accuracy, setting) tuples, SORTED in
      descending order of accuracy.
    """
    
    
    attr = defaultdict(list)
    
    for r in results:
        attr['min_freq='+str(r['min_freq'])].append(r['accuracy'])
        attr['punct='+str(r['punct'])].append(r['accuracy'])


        feature_list2 = []
        
        for f in r['features']:
            feature_list2.append(str(f.__name__))
            
            
        attr['feature='+' '.join(feature_list2)].append(r['accuracy'])
    
    
    acc_result = []
    
    for key,value in attr.items():
        acc_result.append((np.mean(value),key))


    sorted_macc = sorted(acc_result,key = lambda d:-d[0])
    
    # print (sorted_acc)
    
    return sorted_macc


    pass


def fit_best_classifier(docs, labels, best_result):
    """
    Using the best setting from eval_all_combinations,
    re-vectorize all the training data and fit a
    LogisticRegression classifier to all training data.
    (i.e., no cross-validation done here)

    Params:
      docs..........List of training document strings.
      labels........The true labels for each training document (0 or 1)
      best_result...Element of eval_all_combinations
                    with highest accuracy
    Returns:
      clf.....A LogisticRegression classifier fit to all
            training data.
      vocab...The dict from feature name to column index.
    """
    
    
    token = [tokenize(d, keep_internal_punct=best_result["punct"]) for d in docs]
    
    C,vocab = vectorize(token, best_result["features"], best_result['min_freq'])
    
    clf = LogisticRegression()
    clf.fit(C,labels)
    
    return clf,vocab


    pass


def top_coefs(clf, label, n, vocab):
    """
    Find the n features with the highest coefficients in
    this classifier for this label.
    See the .coef_ attribute of LogisticRegression.

    Params:
      clf.....LogisticRegression classifier
      label...1 or 0; if 1, return the top coefficients
              for the positive class; else for negative.
      n.......The number of coefficients to return.
      vocab...Dict from feature name to column index.
    Returns:
      List of (feature_name, coefficient) tuples, SORTED
      in descending order of the coefficient for the
      given class label.
    """
    
    
    reverse_vocab = defaultdict()
    clf_model = clf.coef_[0]

    for key,value in vocab.items():
        reverse_vocab[value] = key

    neg_top_coef = np.argsort(clf_model)[::1][:n]
    pos_top_coef = np.argsort(clf_model)[::-1][:n]
    
    
    
    coef_result = []
    
    if label == 0:
        for n in neg_top_coef:
            if n in reverse_vocab:
                coef_result.append((reverse_vocab[n],abs(clf_model[n])))
        
        sorted_coef = sorted(coef_result,key= lambda x: x[1],reverse = True)
        
        return sorted_coef
    
        
    else:
        for p in pos_top_coef:
            if p in reverse_vocab:
                coef_result.append((reverse_vocab[p],abs(clf_model[p])))
        
        sorted_coef = sorted(coef_result,key= lambda x: x[1],reverse = True)
        
        #print (sorted_coef)

        return sorted_coef
    
    
    pass


def parse_test_data(best_result, vocab):
    """
    Using the vocabulary fit to the training data, read
    and vectorize the testing data. Note that vocab should
    be passed to the vectorize function to ensure the feature
    mapping is consistent from training to testing.

    Note: use read_data function defined above to read the
    test data.

    Params:
      best_result...Element of eval_all_combinations
                    with highest accuracy
      vocab.........dict from feature name to column index,
                    built from the training data.
    Returns:
      test_docs.....List of strings, one per testing document,
                    containing the raw.
      test_labels...List of ints, one per testing document,
                    1 for positive, 0 for negative.
      X_test........A csr_matrix representing the features
                    in the test data. Each row is a document,
                    each column is a feature.
    """
    
    
    docs,labels = read_data(os.path.join('data', 'test'))
    
    best_token = [tokenize(d, keep_internal_punct=best_result['punct']) for d in docs]
    
    X,vocab = vectorize(best_token,best_result['features'],best_result['min_freq'],vocab)
    
    return docs,labels,X


    pass


def print_top_misclassified(test_docs, test_labels, X_test, clf, n):
    """
    Print the n testing documents that are misclassified by the
    largest margin. By using the .predict_proba function of
    LogisticRegression <https://goo.gl/4WXbYA>, we can get the
    predicted probabilities of each class for each instance.
    We will first identify all incorrectly classified documents,
    then sort them in descending order of the predicted probability
    for the incorrect class.
    E.g., if document i is misclassified as positive, we will
    consider the probability of the positive class when sorting.

    Params:
      test_docs.....List of strings, one per test document
      test_labels...Array of true testing labels
      X_test........csr_matrix for test data
      clf...........LogisticRegression classifier fit on all training
                    data.
      n.............The number of documents to print.

    Returns:
      Nothing; see Log.txt for example printed output.
    """
    
    
    mis_result = []
    pred = clf.predict(X_test)
    prob = clf.predict_proba(X_test)


    i = 0
    while i < len(test_docs):
        if pred[i] != test_labels[i]:
            mis_result.append({'truth':test_labels[i],'predicted':pred[i],'probability':prob[i][0],'docs':test_docs[i]})
        i+=1
        
        
    j = 0
    while j < len(test_docs):
        if pred[j] != test_labels[j]:
            mis_result.append({'truth': test_labels[j], 'predicted': pred[j], 'probability': prob[j][1],'docs': test_docs[j]})
        j += 1
        

    k = sorted(mis_result,key = lambda k:k['probability'],reverse = True)[:n]
    
    for l in k:
        print("truth="+str(l['truth']), "predicted="+str(l['predicted']), "proba="+str('%.6f' %l['probability']))
        print(l['docs'],"\n")
        
        
    pass



def main():
    
    
    feature_fns = [token_features, token_pair_features, lexicon_features]
    # Download and read data.
    download_data()
  
    
    docs, labels = read_data(os.path.join('data', 'train'))
    # Evaluate accuracy of many combinations
    # of tokenization/featurization.
    results = eval_all_combinations(docs, labels,
                                    [True, False],
                                    feature_fns,
                                    [2,5,10])
    # Print information about these results.
    best_result = results[0]
    worst_result = results[-1]
    print('best cross-validation result:\n%s' % str(best_result))
    print('worst cross-validation result:\n%s' % str(worst_result))
    plot_sorted_accuracies(results)
    print('\nMean Accuracies per Setting:')
    print('\n'.join(['%s: %.5f' % (s,v) for v,s in mean_accuracy_per_setting(results)]))

    # Fit best classifier.
    clf, vocab = fit_best_classifier(docs, labels, results[0])

    # Print top coefficients per class.
    print('\nTOP COEFFICIENTS PER CLASS:')
    print('negative words:')
    print('\n'.join(['%s: %.5f' % (t,v) for t,v in top_coefs(clf, 0, 5, vocab)]))
    print('\npositive words:')
    print('\n'.join(['%s: %.5f' % (t,v) for t,v in top_coefs(clf, 1, 5, vocab)]))

    # Parse test data
    test_docs, test_labels, X_test = parse_test_data(best_result, vocab)

    # Evaluate on test set.
    predictions = clf.predict(X_test)
    print('testing accuracy=%f' %
          accuracy_score(test_labels, predictions))

    print('\nTOP MISCLASSIFIED TEST DOCUMENTS:')
    print_top_misclassified(test_docs, test_labels, X_test, clf, 5)


if __name__ == '__main__':
    main()
